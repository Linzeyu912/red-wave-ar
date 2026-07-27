# S1 门楼外观资产：GATE-01 v2

> 状态：`DELIVERED_NOT_RUNTIME_INTEGRATED`
> 接收日期：2026-07-27
> 对应规范：`modeling_input/S1/02_MODELING_HANDOFF.md` §8

本目录归档用户提供的已完成门楼模型。它是独立资产，**没有**接入 `app/`、`scene.json` 或当前 S1 地下储洞白盒；当前 App 的运行时资产和资源契约不变。

## 内容与校验

| 文件 | 用途 | 关键数据 |
|---|---|---|
| `runtime/s1_gate_v2.glb` | 已接收的 GLB 交付 | 5,020,356 bytes；SHA-256 `217E9B070E2331E7A4DC8CA584639252BBD8C9E559EA0B19C11780598D8EE92F` |
| `preview/orthographic_v2.png` | 正面、侧面与平面核验图 | 1,219 × 581 px；69,595 bytes |
| `source/build_gate_v2.py` | 归档的程序化生成脚本 | 需要 Python、NumPy、trimesh、Pillow 和可显示中文的字体 |

GLB 为 glTF 2.0，包含 370 个节点、369 个网格、13,722 个三角面、12 个材质和 12 张内嵌 PNG 纹理；未使用 glTF 扩展。

## 当前限制

- 该模型保留了照片启发的旗帜、匾额/楹联和现状入口细节，因此是**待审核的交付归档**，不是可直接发布或上架的正式资产。
- 在集成 App 前，必须按 `GATE-01` 处理：替换或移除不确定的文字与书法、把旗帜设为可关闭装饰、完成版权/来源复核，并针对移动端重新评估网格和纹理预算。
- 参考照片仍只存于 `modeling_input/S1/local_reference/`，由 Git 忽略；不得把照片本身、照片投影或原图纹理加入此资产或 App。

## 重新生成（仅用于内部复核）

```powershell
$env:S1_GATE_FONT = 'C:\Windows\Fonts\msyh.ttc' # 如系统没有可用中文字体则显式指定
python .\modeling_delivery\S1\gate\source\build_gate_v2.py
```

脚本只用于复核已接收模型的生成过程；其 `.build/` 纹理中间文件不入库，重新生成的二进制文件须再次核验并经审核后才能替换当前交付。
