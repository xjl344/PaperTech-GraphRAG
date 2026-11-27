# v3 隔离图路径覆盖审计

状态：`passed`；覆盖 39/40 个有来源题，N06 单列为无语料来源负例；失败 0。
隔离图节点 198、有来源关系声明 204；精确引句 204 条。SHA-256：`f2eaae0c534dfa501b66ed80b5cd94c2140163d7a760acb56babd0218bab5d73`。

| 题号 | 类型 | 来源单元 | 论文数 | 核验关系边 | 状态 |
|---|---|---:|---:|---:|---|
| F01 | fact | 1 | 1 | 2 | covered |
| F02 | fact | 1 | 1 | 3 | covered |
| F03 | fact | 1 | 1 | 7 | covered |
| F04 | fact | 1 | 1 | 5 | covered |
| F05 | fact | 1 | 1 | 7 | covered |
| F06 | fact | 1 | 1 | 6 | covered |
| F07 | fact | 1 | 1 | 4 | covered |
| F08 | fact | 1 | 1 | 4 | covered |
| R01 | cross | 2 | 2 | 8 | covered |
| R02 | cross | 2 | 2 | 10 | covered |
| R03 | cross | 2 | 2 | 12 | covered |
| R04 | cross | 2 | 2 | 7 | covered |
| R05 | cross | 2 | 2 | 7 | covered |
| R06 | cross | 2 | 2 | 8 | covered |
| R07 | cross | 2 | 2 | 12 | covered |
| R08 | cross | 3 | 2 | 9 | covered |
| R09 | cross | 2 | 2 | 14 | covered |
| R10 | cross | 4 | 2 | 19 | covered |
| R11 | cross | 2 | 2 | 13 | covered |
| R12 | cross | 2 | 2 | 9 | covered |
| R13 | cross | 2 | 2 | 16 | covered |
| R14 | cross | 2 | 2 | 14 | covered |
| R15 | cross | 2 | 2 | 11 | covered |
| R16 | cross | 2 | 2 | 9 | covered |
| R17 | cross | 2 | 2 | 7 | covered |
| R18 | cross | 2 | 2 | 8 | covered |
| R19 | cross | 3 | 3 | 14 | covered |
| R20 | cross | 3 | 3 | 16 | covered |
| R21 | cross | 3 | 3 | 14 | covered |
| R22 | cross | 3 | 3 | 14 | covered |
| R23 | cross | 2 | 2 | 13 | covered |
| R24 | cross | 3 | 2 | 11 | covered |
| N01 | negative | 2 | 2 | 10 | covered |
| N02 | negative | 2 | 2 | 14 | covered |
| N03 | negative | 2 | 2 | 12 | covered |
| N04 | negative | 2 | 2 | 13 | covered |
| N05 | negative | 2 | 2 | 7 | covered |
| N06 | negative | 0 | 0 | 0 | negative_anchor_absence_checked |
| N07 | negative | 2 | 2 | 12 | covered |
| N08 | negative | 2 | 2 | 11 | covered |

## 范围限制

- 关系图针对冻结的 40 题和 25 个已核查来源单元，不是对全部 980 个块的穷尽抽取。
- 每条边均保留整块精确原文及页码；审核是来源核对，不是独立人工专家审查。
- N06 的零来源检查不能证明语料外或未来材料中不存在该名称。
