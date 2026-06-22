# babel-plugin-tester 源码学习笔记

## 核心架构设计

### 1. 错误处理模式 - ErrorMessage 对象

**设计模式**：集中式错误消息工厂

```typescript
export const ErrorMessage = {
  TestEnvironmentUndefinedDescribe: () =>
    'incompatible testing environment: testing environment must define `describe` in its global scope',
  BadConfigPluginAndPreset: () =>
    'failed to validate configuration: cannot test a plugin and a preset simultaneously',
  ExpectedErrorToIncludeString: (resultString: string, expectedError: string) =>
    `expected "${resultString}" to include "${expectedError}"`,
  // ... 更多错误消息
};
```

**优点**：
- 错误消息集中管理，易于维护
- 支持参数化消息（函数工厂模式）
- 类型安全的错误生成
- 便于国际化/本地化

**应用场景**：
- 大型项目的错误处理
- 需要详细错误信息的库/框架
- 测试框架的断言失败消息

---

### 2. Symbol 作为 API 协议

**设计模式**：使用 unique symbol 作为插件/预设的占位符

```typescript
const runPluginUnderTestHere: unique symbol = Symbol.for(
  '@xunnamius/run-plugin-under-test-here'
);

const runPresetUnderTestHere: unique symbol = Symbol.for(
  '@xunnamius/run-preset-under-test-here'
);
```

**用途**：
```typescript
babelOptions: {
  plugins: [
    someOtherPlugin,
    runPluginUnderTestHere,  // 插入点标记
    anotherPlugin
  ]
}
```

**优点**：
- 类型安全且不会与任何值冲突
- Symbol.for() 允许跨模块共享
- 清晰的语义：这是一个协议而非数据
- 允许用户自定义插件运行顺序

---

### 3. 全局环境检测模式

**设计模式**：检测全局对象而非硬编码依赖

```typescript
const globalContextHasExpectFn =
  'expect' in globalThis && typeof expect === 'function';

const globalContextHasDescribeFn =
  'describe' in globalThis && typeof describe === 'function';

const globalContextExpectFnHasToMatchSnapshot = (() => {
  try {
    return globalContextHasExpectFn
      ? typeof expect(undefined).toMatchSnapshot === 'function'
      : false;
  } catch {
    return false;
  }
})();
```

**优点**：
- 跨测试框架兼容（Jest, Mocha, Vitest 等）
- 无硬编码依赖
- 优雅降级
- 运行时能力检测

---

### 4. 配置合并策略 - Lodash mergeWith

**设计模式**：基础配置 + 测试配置 → 最终配置

```typescript
const baseConfig: PluginTesterBaseConfig = mergeWith(
  {
    formatResult: ((r) => r) as ResultFormatter,
    snapshot: false,
    fixtureOutputName: 'output',
    setup: noop,
    teardown: noop
  },
  options,
  mergeCustomizer
);
```

**自定义合并器**：
```typescript
const mergeCustomizer = (
  objValue: unknown,
  srcValue: unknown,
  key: string
): unknown => {
  // 特殊处理：数组覆盖而非合并
  if (Array.isArray(objValue) && Array.isArray(srcValue)) {
    return srcValue;
  }
  // 其他情况使用默认合并行为
  return undefined;
};
```

---

### 5. 快照序列化器模式

**问题**：Jest 快照会序列化字符串为 `"\"content\""`，产生多余的转义引号

**解决方案**：自定义序列化器

```typescript
export const unstringSnapshotSerializer: SnapshotSerializer = {
  test: (value: unknown) => typeof value === 'string',
  print: (value: unknown) => String(value)
};

// 全局注册
if ('expect' in globalThis && typeof expect.addSnapshotSerializer === 'function') {
  expect.addSnapshotSerializer(unstringSnapshotSerializer);
}
```

---

### 6. 文件路径自动推断

**技术**：通过 Error.stack 解析调用栈获取文件路径

```typescript
function tryInferFilepath() {
  const oldStackTraceLimit = Error.stackTraceLimit;
  Error.stackTraceLimit = Number.POSITIVE_INFINITY;

  try {
    const reversedCallStack = (
      new Error('faux error').stack
        ?.split('\n')
        .map(line => {
          const { fn: functionName, path: filePath } =
            line.match(parseErrorStackRegExp)?.groups || {};
          
          return filePath ? { functionName, filePath } : undefined;
        })
        .filter(Boolean)
        .toReversed()
    );

    // 查找调用 pluginTester 的文件
    for (const { filePath } of reversedCallStack) {
      if (parseScriptFilepathRegExp.test(filePath)) continue;
      return filePath;
    }
  } finally {
    Error.stackTraceLimit = oldStackTraceLimit;
  }
}
```

**优点**：
- 减少用户配置负担
- 自动解析相对路径
- 无需显式传递 __filename

---

### 7. 调试器分层设计

**模式**：使用 rejoinder 库的 extend 方法创建分层调试命名空间

```typescript
const { debug: debug1, verbose: verbose1 } = getDebuggers('tester', globalDebugger);
const { debug: debug2, verbose: verbose2 } = getDebuggers('config', debug1);
const { debug: debug3, verbose: verbose3 } = getDebuggers('create-fix', debug2);

// 使用
debug1('executing main babel-plugin-tester function');
debug2('running in plugin mode');
debug3('potentially generating test objects from fixture');
```

**命名空间层级**：
- `bpt` - 全局命名空间
- `bpt:tester` - 主测试器
- `bpt:tester:config` - 配置处理
- `bpt:tester:config:create-fix` - Fixture 创建

**启用调试**：
```bash
DEBUG=bpt:tester:config node test.js
DEBUG=bpt:* node test.js  # 所有命名空间
```

---

### 8. 测试编号自动重置

**模式**：模块级计数器 + 重置函数

```typescript
let currentTestNumber = 1;

function restartTestTitleNumbering() {
  debug1('restarted title numbering');
  currentTestNumber = 1;
}

// 使用
if (rawBaseConfig.restartTitleNumbering) {
  restartTestTitleNumbering();
}
```

---

### 9. Fixture 文件系统驱动测试

**目录结构**：
```
fixtures/
  ├── test-name/
  │   ├── code.js          # 输入代码
  │   ├── output.js        # 期望输出
  │   ├── options.json     # 测试选项
  │   └── .babelrc         # 局部 Babel 配置
  └── nested/
      └── describe-block/
          └── code.js
```

**自动发现逻辑**：
```typescript
fs.readdirSync(fixturesDirectory).forEach(filename => {
  const fixtureSubdir = toPath(fixturesDirectory, filename);
  
  // 查找 code.* 或 exec.* 文件
  const codeFilename = directoryFiles.find(f => f.name.startsWith('code.'))?.name;
  const execFilename = directoryFiles.find(f => f.name.startsWith('exec.'))?.name;
  
  // 没有代码文件 → 递归扫描嵌套 fixtures
  if (!codeFilename && !execFilename) {
    createAndPushFixtureConfigs({
      fixturesDirectory: fixtureSubdir,
      fixtureOptions: localOptions,
      parentDescribeConfig: createAndPushDescribeConfig(blockTitle)
    });
  }
});
```

---

### 10. EOL 跨平台处理

```typescript
type EndOfLineOption = 'lf' | 'crlf' | 'auto' | 'preserve' | false;

function trimAndFixLineEndings(
  text: string,
  endOfLine: EndOfLineOption,
  referenceText?: string
): string {
  if (endOfLine === false) return text;
  
  const normalized = text.replace(/\r\n?/g, '\n').trim();
  
  switch (endOfLine) {
    case 'lf':
      return normalized.replace(/\n/g, '\n');
    case 'crlf':
      return normalized.replace(/\n/g, '\r\n');
    case 'auto':
      return normalized.replace(/\n/g, EOL);
    case 'preserve':
      return referenceText 
        ? normalized.replace(/\n/g, detectLineEnding(referenceText))
        : normalized;
    default:
      return normalized;
  }
}
```

---

## 学到的技巧总结

### 类型设计

1. **Symbol 作为协议**：用 unique symbol 作为 API 协议，类型安全且不会冲突
2. **Union 类型穷举**：`'all' | 'tests-only' | 'fixtures-only' | false` 强制处理所有分支
3. **类型安全的 Babel 集成**：
```typescript
babelOptions?: Omit<Babel.TransformOptions, 'plugins' | 'presets'> & {
  plugins?: (Babel.PluginItem | typeof runPluginUnderTestHere)[];
  presets?: (Babel.PresetItem | typeof runPresetUnderTestHere)[];
};
```

### 配置设计

4. **渐进式配置**：`base + override` 模式让默认值可覆盖
5. **智能默认值**：从调用栈自动推断 filepath，从函数名推断 pluginName
6. **环境变量过滤**：`TEST_ONLY=1,3,5` 和 `TEST_SKIP=2,4` 控制测试执行

### 测试框架设计

7. **全局检测**：`'expect' in globalThis` 检测测试框架，而非硬编码依赖
8. **文件系统即测试**：Fixture 模式让测试数据与代码分离，易于维护
9. **错误断言灵活性**：5种 ErrorExpectation 模式覆盖所有场景
10. **Setup/Teardown 链式清理**：setup 返回 teardown，框架自动调用

---

## 源码位置参考

- **错误消息**：`src/errors.ts`
- **核心测试器**：`src/plugin-tester.ts` (1700+ 行)
- **类型定义**：`src/types.ts`
- **常量定义**：`src/constant.ts`
- **Prettier 格式化**：`src/formatters/prettier.ts`
- **快照序列化**：`src/serializers/unstring-snapshot.ts`

---

## 应用启示

这些设计模式可以直接应用到：

1. **测试工具开发**：ErrorMessage 模式、Symbol 协议、全局检测
2. **Babel 插件开发**：理解测试框架如何验证插件输出
3. **CLI 工具开发**：配置合并、文件路径推断、调试器分层
4. **通用库设计**：渐进式配置、智能默认值、错误消息工厂
