# Suggested parallel workstreams

Use one branch and one chat/worker per workstream. Keep scope narrow enough that workers rarely touch the same files.

| Workstream | Suggested branch | Scope |
|---|---|---|
| Array core | `rules/array-core` | Array constructor, length, push/pop/shift/unshift, slice/splice, concat |
| Array iteration | `rules/array-iteration` | map/filter/reduce/find/some/every/forEach |
| String | `rules/string-core` | indexing, slicing, includes, replace, casing, split, trim |
| RegExp | `rules/regexp` | construction, test, exec, flags, match/replace interactions |
| Operators | `rules/operators` | arithmetic, logical, nullish, optional chaining, bitwise |
| Coercion | `rules/coercion` | ToBoolean, ToNumber, ToString, abstract equality |
| Values | `rules/values` | undefined, null, NaN, Infinity, -0, Symbol, BigInt |
| Objects | `rules/objects` | property access, descriptors, spread, Object.* |
| Functions | `rules/functions` | calls, closures, this, bind/call/apply, arrows |
| Classes/prototypes | `rules/classes-prototypes` | class syntax, inheritance, prototype chain |
| Collections | `rules/collections` | Map, Set, WeakMap, WeakSet |
| Async | `rules/async` | Promise, async/await, microtask ordering |
| Iteration | `rules/iteration` | iterators, generators, for...of |
| Errors | `rules/errors` | throw/catch/finally, Error types, stack caveats |
| JSON/Math | `rules/json-math` | JSON, Math, numeric behavior |
| Date | `rules/date` | Date construction, parsing, timezone-sensitive behavior |
| Modules | `rules/modules` | ESM/import/export, CommonJS/require |
| Node fs/path/os | `rules/node-core` | fs, path, os basics |
| Node events/streams | `rules/node-events-streams` | EventEmitter and streams |
| Electron core | `rules/electron-core` | BrowserWindow, app lifecycle, ipcMain/ipcRenderer |
| Electron OS APIs | `rules/electron-os` | dialog, shell, clipboard, tray, notifications, shortcuts |

## Merge order suggestion

Start with values/coercion/operators before aggressively marking higher-level APIs as native. Many apparently simple APIs depend on JavaScript coercion semantics.

Each PR should add rules plus enough tests to demonstrate why its selected translation tier is sound.
