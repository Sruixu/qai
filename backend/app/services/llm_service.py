from typing import List, Dict, Any, Optional
import json
import re
from langchain_openai import ChatOpenAI
from app.core.vector_store import vector_store

class LLMService:
    def __init__(self):
        pass

    def _get_llm(self, api_key: str, base_url: str, model: str):
        if not api_key and base_url: # Allow custom proxies without key if they support it
             pass 
        elif not api_key:
            return None
            
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key if api_key else "sk-placeholder", # Some local LLMs need non-empty key
            openai_api_base=base_url,
            temperature=0.7
        )

    def _parse_json_response(self, content: str) -> Any:
        try:
            # 1. Try to find JSON in markdown code blocks
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if match:
                content = match.group(1)
            else:
                # 2. Try to find the first '[' or '{' and last ']' or '}'
                # This handles cases where models output "Sure, here is the JSON: [...]" without markdown
                content = content.strip()
                start_bracket = content.find('[')
                start_brace = content.find('{')
                
                start_index = -1
                end_index = -1
                
                # Determine if we are looking for array or object
                if start_bracket != -1 and (start_brace == -1 or start_bracket < start_brace):
                    start_index = start_bracket
                    end_index = content.rfind(']') + 1
                elif start_brace != -1:
                    start_index = start_brace
                    end_index = content.rfind('}') + 1
                    
                if start_index != -1 and end_index != -1:
                    content = content[start_index:end_index]

            # 3. Clean up potential comments or trailing commas (simple approach)
            # Remove "// ..." comments
            content = re.sub(r'//.*', '', content)
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}, raw content: {content}")
            # Try a very aggressive fallback: maybe it's valid python dict string?
            try:
                import ast
                return ast.literal_eval(content)
            except:
                pass
            return []

    def generate_test_cases(
        self, 
        requirement_content: str, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None, 
        model: str = "deepseek-chat"
    ) -> List[Dict[str, Any]]:
        """Legacy One-Shot Generation"""
        llm = self._get_llm(api_key, base_url, model)
        
        # 1. Retrieve Historical Context (RAG)
        similar_docs = vector_store.query_similar(requirement_content, n_results=3)
        context_str = ""
        if similar_docs:
            context_str = "参考以下历史相似需求及其测试用例（Knowledge Base）：\n\n"
            for doc in similar_docs:
                context_str += f"--- 历史需求 ---\n{doc['content']}\n"
                context_str += f"--- 关联用例 ---\n{doc['metadata'].get('cases_json', '无')}\n\n"
        
        system_prompt = """你是一位资深测试工程师。请根据给定的[当前需求]，参考[历史知识库]（如果有），编写详细的测试用例。
        
输出必须是纯 JSON 数组格式，不要包含 Markdown 代码块标记，每个对象包含以下字段：
- module: 模块名称
- title: 用例标题
- priority: 优先级 (P0/P1/P2/P3)
- precondition: 前置条件
- steps: 操作步骤 (使用 1. 2. 3. 换行)
- expected_result: 预期结果

请确保覆盖正常路径、异常路径和边界值。
"""
        user_prompt = f"""
{context_str}

=== 当前需求 ===
{requirement_content}

请生成测试用例：
"""
        if llm:
            try:
                messages = [("system", system_prompt), ("human", user_prompt)]
                response = llm.invoke(messages)
                return self._parse_json_response(response.content)
            except Exception as e:
                print(f"LLM Call failed: {e}")
                return self._mock_fallback(requirement_content)
        else:
            return self._mock_fallback(requirement_content)

    # --- Sakura-Style 3-Stage Generation ---

    def analyze_modules(self, requirement_content: str, api_key: str, base_url: str, model: str) -> List[str]:
        """Step 1: Identify functional modules"""
        llm = self._get_llm(api_key, base_url, model)
        if not llm: return ["默认模块"]

        system_prompt = "你是一名产品经理。请分析需求文档，将其拆分为3-6个独立的功能模块。只输出JSON字符串数组，例如 [\"用户登录\", \"订单管理\"]。严禁输出任何解释性文字或Markdown格式之外的内容。"
        user_prompt = f"需求内容：\n{requirement_content}"
        
        try:
            response = llm.invoke([("system", system_prompt), ("human", user_prompt)])
            return self._parse_json_response(response.content)
        except Exception as e:
            print(f"Analyze modules failed: {e}")
            return ["功能模块A", "功能模块B"]

    def generate_scenarios(self, requirement_content: str, module: str, api_key: str, base_url: str, model: str) -> List[str]:
        """Step 2: Generate test scenarios for a module"""
        llm = self._get_llm(api_key, base_url, model)
        if not llm: return ["默认场景"]

        system_prompt = f"你是一名测试架构师。针对模块【{module}】，识别2-8个关键测试场景（Test Scenarios/Purposes）。只输出JSON字符串数组，例如 [\"验证手机号登录\", \"验证密码错误提示\"]。严禁输出任何解释性文字。"
        user_prompt = f"需求内容：\n{requirement_content}"

        try:
            response = llm.invoke([("system", system_prompt), ("human", user_prompt)])
            return self._parse_json_response(response.content)
        except Exception as e:
            print(f"Generate scenarios failed: {e}")
            return [f"{module}-场景1", f"{module}-场景2"]

    def generate_test_cases_rag(
        self, 
        requirement_content: str, 
        module: str, 
        scenario: str, 
        api_key: str, 
        base_url: str, 
        model: str
    ) -> List[Dict[str, Any]]:
        """Step 3: Generate detailed cases for a scenario with RAG"""
        llm = self._get_llm(api_key, base_url, model)
        if not llm: return self._mock_fallback(requirement_content)[:1]

        # RAG Retrieval focused on the scenario if possible, but we only have reqs indexed
        similar_docs = vector_store.query_similar(f"{module} {scenario}", n_results=2)
        context_str = ""
        if similar_docs:
            context_str = "参考历史经验（注意历史中的边界值和坑）：\n"
            for doc in similar_docs:
                context_str += f"- 历史需求: {doc['content'][:100]}...\n- 关联用例片段: {doc['metadata'].get('cases_json', '')[:200]}...\n"

        system_prompt = f"""你是一名高级测试工程师。针对模块【{module}】下的场景【{scenario}】，编写详细测试用例。
必须输出纯 JSON 数组，严禁输出任何解释性文字。字段：
- module: 固定为 "{module}"
- title: 用例标题
- priority: P0/P1/P2
- precondition: 前置条件
- steps: 详细步骤
- expected_result: 预期结果
"""
        user_prompt = f"""
{context_str}

=== 当前需求 ===
{requirement_content}

请为场景【{scenario}】生成 1-3 个具体的测试用例：
"""
        try:
            response = llm.invoke([("system", system_prompt), ("human", user_prompt)])
            return self._parse_json_response(response.content)
        except Exception as e:
            print(f"Generate cases RAG failed: {e}")
            return self._mock_fallback(requirement_content)[:1]

    def generate_automation_script(self, test_case: Dict, api_key: str, base_url: str, model: str) -> str:
        """Generate Playwright Python script"""
        llm = self._get_llm(api_key, base_url, model)
        if not llm: return "# No LLM configured"

        system_prompt = """你是一个自动化测试专家。将给定的测试用例步骤转换为 Python Playwright (Sync API) 代码。
只输出代码内容，不要Markdown标记。假设已有 page 对象。不要包含 browser 启动代码，只包含测试步骤逻辑。
"""
        user_prompt = f"""
用例标题: {test_case.get('title')}
前置条件: {test_case.get('precondition')}
步骤:
{test_case.get('steps')}
预期结果:
{test_case.get('expected_result')}
"""
        try:
            response = llm.invoke([("system", system_prompt), ("human", user_prompt)])
            content = response.content
            # 1. Try to find Python code in markdown code blocks
            match = re.search(r'```(?:python)?\s*([\s\S]*?)\s*```', content)
            if match:
                content = match.group(1)
            else:
                # 2. Heuristic: Remove lines that don't look like code (simplified)
                # Or just strip typical "Here is the code:" prefixes
                content = re.sub(r'^[\s\S]*?import ', 'import ', content) # Start from first import if possible
                content = re.sub(r'^[\s\S]*?from ', 'from ', content)
            
            return content.strip()
        except Exception as e:
            return f"# Generate script failed: {e}"

    def _mock_fallback(self, requirement_content: str):
        cases = []
        cases.append({
            "module": "Mock模块",
            "title": "Mock测试用例",
            "precondition": "无",
            "steps": "1. 步骤一\n2. 步骤二",
            "expected_result": "成功",
            "priority": "P1"
        })
        return cases

llm_service = LLMService()
