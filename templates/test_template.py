"""
测试 {{test_module_name}} 模块

此测试文件验证 {{test_target}} 的功能和边界情况。
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

from {{import_path}} import {{class_name}}
{{additional_imports}}


class Test{{class_name}}:
    """测试 {{class_name}} 类"""

    # ==================== Fixtures ====================

    @pytest.fixture
    def {{fixture_name}}(self):
        """创建测试用的 {{fixture_description}}

        Returns:
            {{fixture_return_type}}: {{fixture_return_description}}
        """
        # TODO: 创建测试对象
        {{fixture_object}} = {{class_name}}(
            {{fixture_param_1}}={{fixture_value_1}},
            {{fixture_param_2}}={{fixture_value_2}}
        )
        return {{fixture_object}}

    @pytest.fixture
    def {{mock_fixture_name}}(self):
        """创建模拟的 {{mock_description}}

        Returns:
            MagicMock: {{mock_return_description}}
        """
        mock = MagicMock()
        # TODO: 配置 mock 对象
        mock.{{mock_attribute}}.return_value = {{mock_return_value}}
        return mock

    # ==================== 基础功能测试 ====================

    def test_{{test_case_1_name}}(self, {{fixture_name}}):
        """测试 {{test_case_1_description}}

        Given: {{given_condition_1}}
        When: {{when_action_1}}
        Then: {{then_expected_1}}
        """
        # Given: 设置测试条件
        {{setup_code_1}}

        # When: 执行操作
        result = {{fixture_name}}.{{method_under_test}}({{test_param_1}})

        # Then: 验证结果
        assert result == {{expected_result_1}}
        assert {{fixture_name}}.{{attribute_1}} == {{expected_value_1}}

    def test_{{test_case_2_name}}(self, {{fixture_name}}):
        """测试 {{test_case_2_description}}

        Given: {{given_condition_2}}
        When: {{when_action_2}}
        Then: {{then_expected_2}}
        """
        # Given
        {{setup_code_2}}

        # When
        result = {{fixture_name}}.{{method_under_test}}({{test_param_2}})

        # Then
        assert result == {{expected_result_2}}

    # ==================== 边界情况测试 ====================

    def test_{{edge_case_1_name}}(self, {{fixture_name}}):
        """测试边界情况: {{edge_case_1_description}}

        验证当 {{edge_condition_1}} 时，系统行为正确。
        """
        # Given: 边界条件
        {{edge_setup_1}}

        # When: 执行操作
        result = {{fixture_name}}.{{method_under_test}}({{edge_param_1}})

        # Then: 验证边界行为
        assert result == {{edge_expected_1}}

    def test_{{edge_case_2_name}}(self, {{fixture_name}}):
        """测试边界情况: {{edge_case_2_description}}"""
        # Given
        {{edge_setup_2}}

        # When
        with pytest.raises({{expected_exception}}):
            {{fixture_name}}.{{method_under_test}}({{edge_param_2}})

    # ==================== 异常处理测试 ====================

    def test_{{exception_case_1_name}}(self, {{fixture_name}}):
        """测试异常处理: {{exception_case_1_description}}

        验证当 {{exception_condition_1}} 时，抛出正确的异常。
        """
        # Given: 异常触发条件
        {{exception_setup_1}}

        # Then: 验证异常
        with pytest.raises({{exception_type_1}}) as exc_info:
            {{fixture_name}}.{{method_under_test}}({{exception_param_1}})

        assert "{{expected_error_message}}" in str(exc_info.value)

    def test_{{exception_case_2_name}}(self, {{fixture_name}}):
        """测试异常处理: {{exception_case_2_description}}"""
        # Given
        {{exception_setup_2}}

        # Then
        with pytest.raises({{exception_type_2}}):
            {{fixture_name}}.{{method_under_test}}({{exception_param_2}})

    # ==================== Mock 对象测试 ====================

    def test_{{mock_case_1_name}}(self, {{fixture_name}}, {{mock_fixture_name}}):
        """测试与依赖的交互: {{mock_case_1_description}}

        验证方法正确调用了依赖对象。
        """
        # Given: 使用 mock 对象
        {{fixture_name}}.{{dependency_attribute}} = {{mock_fixture_name}}

        # When: 执行操作
        {{fixture_name}}.{{method_under_test}}({{mock_param_1}})

        # Then: 验证调用
        {{mock_fixture_name}}.{{expected_method}}.assert_called_once_with({{expected_args}})

    @patch('{{module_path}}.{{patched_class}}')
    def test_{{patch_case_1_name}}(self, mock_{{patched_class_lower}}, {{fixture_name}}):
        """测试使用 patch 的场景: {{patch_case_1_description}}"""
        # Given: 配置 patch
        mock_{{patched_class_lower}}.return_value = {{mock_return_value}}

        # When: 执行操作
        result = {{fixture_name}}.{{method_under_test}}()

        # Then: 验证结果和调用
        assert result == {{expected_result}}
        mock_{{patched_class_lower}}.assert_called()

    # ==================== 异步测试 ====================

    @pytest.mark.asyncio
    async def test_{{async_case_1_name}}(self, {{fixture_name}}):
        """测试异步方法: {{async_case_1_description}}

        验证异步操作正确执行。
        """
        # Given: 异步测试条件
        {{async_setup_1}}

        # When: 执行异步操作
        result = await {{fixture_name}}.{{async_method}}({{async_param_1}})

        # Then: 验证结果
        assert result == {{async_expected_1}}

    @pytest.mark.asyncio
    async def test_{{async_case_2_name}}(self, {{fixture_name}}):
        """测试异步异常处理: {{async_case_2_description}}"""
        # Given
        {{async_setup_2}}

        # Then
        with pytest.raises({{async_exception_type}}):
            await {{fixture_name}}.{{async_method}}({{async_param_2}})

    # ==================== 参数化测试 ====================

    @pytest.mark.parametrize("{{param_name}},{{expected_name}}", [
        ({{param_value_1}}, {{expected_value_1}}),
        ({{param_value_2}}, {{expected_value_2}}),
        ({{param_value_3}}, {{expected_value_3}}),
    ])
    def test_{{parametrize_case_name}}(self, {{fixture_name}}, {{param_name}}, {{expected_name}}):
        """参数化测试: {{parametrize_description}}

        测试不同输入值的输出结果。
        """
        # When
        result = {{fixture_name}}.{{method_under_test}}({{param_name}})

        # Then
        assert result == {{expected_name}}

    # ==================== 集成测试 ====================

    def test_{{integration_case_1_name}}(self, {{fixture_name}}):
        """集成测试: {{integration_case_1_description}}

        测试多个方法的组合使用。
        """
        # Given: 初始状态
        {{integration_setup_1}}

        # When: 执行一系列操作
        {{fixture_name}}.{{method_1}}({{param_1}})
        {{fixture_name}}.{{method_2}}({{param_2}})
        result = {{fixture_name}}.{{method_3}}({{param_3}})

        # Then: 验证最终状态
        assert result == {{integration_expected_1}}
        assert {{fixture_name}}.{{state_attribute}} == {{expected_state}}


class Test{{class_name}}Edge:
    """测试 {{class_name}} 的边界和特殊场景"""

    def test_{{special_case_1_name}}(self):
        """测试特殊场景: {{special_case_1_description}}"""
        # TODO: 实现特殊场景测试
        pass

    def test_{{special_case_2_name}}(self):
        """测试特殊场景: {{special_case_2_description}}"""
        # TODO: 实现特殊场景测试
        pass


# ==================== 辅助函数测试 ====================

def test_{{helper_function_name}}():
    """测试辅助函数: {{helper_function_description}}"""
    # Given
    {{helper_setup}}

    # When
    result = {{helper_function_name}}({{helper_param}})

    # Then
    assert result == {{helper_expected}}
