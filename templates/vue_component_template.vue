<script setup lang="ts">
/**
 * {{component_description}}
 *
 * 功能:
 * - {{feature_1}}
 * - {{feature_2}}
 * - {{feature_3}}
 *
 * Props:
 * - {{prop_name_1}}: {{prop_description_1}}
 * - {{prop_name_2}}: {{prop_description_2}}
 *
 * Emits:
 * - {{emit_name_1}}: {{emit_description_1}}
 * - {{emit_name_2}}: {{emit_description_2}}
 *
 * 使用示例:
 * ```vue
 * <{{component_name}}
 *   :{{prop_name_1}}="{{example_prop_value_1}}"
 *   :{{prop_name_2}}="{{example_prop_value_2}}"
 *   @{{emit_name_1}}="{{example_handler_1}}"
 *   @{{emit_name_2}}="{{example_handler_2}}"
 * />
 * ```
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import type { {{type_import_1}}, {{type_import_2}} } from '@/types/{{type_module}}'

// Props 定义
interface Props {
  /** {{prop_description_1}} */
  {{prop_name_1}}: {{prop_type_1}}

  /** {{prop_description_2}} */
  {{prop_name_2}}?: {{prop_type_2}}
}

// Emits 定义
interface Emits {
  /** {{emit_description_1}} */
  (e: '{{emit_name_1}}', {{emit_param_1}}: {{emit_param_type_1}}): void

  /** {{emit_description_2}} */
  (e: '{{emit_name_2}}', {{emit_param_2}}: {{emit_param_type_2}}): void
}

const props = withDefaults(defineProps<Props>(), {
  {{prop_name_2}}: {{prop_default_value_2}}
})

const emit = defineEmits<Emits>()

// ==================== 响应式状态 ====================

/** {{state_description_1}} */
const {{state_name_1}} = ref<{{state_type_1}}>({{state_initial_value_1}})

/** {{state_description_2}} */
const {{state_name_2}} = ref<{{state_type_2}}>({{state_initial_value_2}})

// ==================== 计算属性 ====================

/**
 * {{computed_description_1}}
 */
const {{computed_name_1}} = computed(() => {
  // TODO: 实现计算逻辑
  return {{computed_return_value_1}}
})

/**
 * {{computed_description_2}}
 */
const {{computed_name_2}} = computed(() => {
  // TODO: 实现计算逻辑
  return {{computed_return_value_2}}
})

// ==================== 方法 ====================

/**
 * {{method_description_1}}
 * @param {{method_param_1}} - {{method_param_description_1}}
 */
function {{method_name_1}}({{method_param_1}}: {{method_param_type_1}}): void {
  // TODO: 实现方法逻辑

  // 示例：更新状态
  // {{state_name_1}}.value = {{new_value}}

  // 示例：触发事件
  // emit('{{emit_name_1}}', {{emit_value}})
}

/**
 * {{method_description_2}}
 */
async function {{method_name_2}}(): Promise<void> {
  try {
    // TODO: 实现异步逻辑

    // 示例：API 调用
    // const result = await {{api_call}}()
    // {{state_name_2}}.value = result

  } catch (error) {
    console.error('{{error_context}}:', error)
    // TODO: 错误处理
  }
}

/**
 * {{handler_description}}
 * @param event - {{event_description}}
 */
function {{handler_name}}(event: {{event_type}}): void {
  // TODO: 实现事件处理逻辑

  // 示例：阻止默认行为
  // event.preventDefault()

  // 示例：处理事件
  // const {{extracted_data}} = event.{{data_property}}
  // {{method_name_1}}({{extracted_data}})
}

// ==================== 生命周期钩子 ====================

/**
 * 组件挂载时执行
 */
onMounted(() => {
  // TODO: 初始化逻辑

  // 示例：加载数据
  // {{method_name_2}}()

  // 示例：添加事件监听
  // window.addEventListener('{{event_name}}', {{handler_name}})
})

/**
 * 组件卸载时执行
 */
onUnmounted(() => {
  // TODO: 清理逻辑

  // 示例：移除事件监听
  // window.removeEventListener('{{event_name}}', {{handler_name}})
})

// ==================== 监听器 ====================

/**
 * 监听 {{prop_name_1}} 变化
 */
watch(() => props.{{prop_name_1}}, (newValue, oldValue) => {
  // TODO: 实现监听逻辑

  // 示例：响应 prop 变化
  // if (newValue !== oldValue) {
  //   {{method_name_2}}()
  // }
})
</script>

<template>
  <div class="{{component_class_name}}">
    <!-- TODO: 实现模板 -->

    <!-- 示例：标题 -->
    <div class="{{component_class_name}}__header">
      <h2>{{component_title}}</h2>
    </div>

    <!-- 示例：内容区域 -->
    <div class="{{component_class_name}}__content">
      <!-- 示例：条件渲染 -->
      <div v-if="{{computed_name_1}}">
        {{content_when_true}}
      </div>
      <div v-else>
        {{content_when_false}}
      </div>

      <!-- 示例：列表渲染 -->
      <div
        v-for="{{item}} in {{state_name_2}}"
        :key="{{item}}.{{item_key_property}}"
        class="{{component_class_name}}__item"
        @click="{{method_name_1}}({{item}})"
      >
        {{ {{item}}.{{item_display_property}} }}
      </div>
    </div>

    <!-- 示例：操作按钮 -->
    <div class="{{component_class_name}}__actions">
      <button
        class="btn primary"
        @click="{{method_name_2}}"
        :disabled="{{computed_name_2}}"
      >
        {{button_text_1}}
      </button>
      <button
        class="btn"
        @click="emit('{{emit_name_2}}', {{emit_value}})"
      >
        {{button_text_2}}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.{{component_class_name}} {
  // TODO: 添加样式

  // 示例：容器样式
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background);
  border-radius: 8px;

  &__header {
    // 示例：头部样式
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);

    h2 {
      margin: 0;
      font-size: 1.5rem;
      color: var(--color-text-primary);
    }
  }

  &__content {
    // 示例：内容区域样式
    flex: 1;
    overflow-y: auto;
  }

  &__item {
    // 示例：列表项样式
    padding: 0.5rem;
    cursor: pointer;
    border-radius: 4px;
    transition: background 0.2s;

    &:hover {
      background: var(--color-hover);
    }
  }

  &__actions {
    // 示例：操作区域样式
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    padding-top: 0.5rem;
    border-top: 1px solid var(--color-border);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .{{component_class_name}} {
    padding: 0.5rem;

    &__actions {
      flex-direction: column;

      button {
        width: 100%;
      }
    }
  }
}
</style>
