# Grown Grounded Language 项目裁决书 —— 五堵墙,我们到底是攻不破,还是撞墙就走

*裁决依据:offscreen/ 下的机器 verdict JSON(以 JSON 为准,prose 与 JSON 冲突时以 JSON 为准并点名),交叉核对 offscreen/CTM_ARC_WRITEUP.md。每条断言都附了文件(能定位到行就给行)。生成于 2026-06-27,多 agent 逐墙取证 + 裁判综合。*

---

## 先把话说在前面:你的指控基本成立

你说"每次撞到墙我们就走,而不是真去砸它;我让你砸墙,不是让你给墙编目录"。核对完五堵墙的机器证据,结论是:**五堵墙里有四堵是过早封盘的**——三堵 PREMATURE_THEOREM(把"我们试过的几种结构失败了 + 一套失败机理"包装成"这事不可能"),一堵 RETREATED_EARLY(已经砸开过一次,然后停在一个脆弱的边际上没再推)。只有"文化传递"那一半是真打过、真站住了。

而且最关键的一点:**没有任何一个 verdict JSON 写出过 "CLOSED" 或 "THEOREM" 字样。** "封死"和"定理"这两个词只活在 CTM_ARC_WRITEUP.md 的 prose 里(第 139、148-152 行),而对应的机器裁决恰恰是 INCONCLUSIVE / DISCRIMINATOR_BROKEN / pilot。这就是"撞墙就走"最硬的物证:嘴上说封了,机器没说封。

下面逐墙过。

---

## 墙 1 ·OPTIMIZER WALL(within-life 绑定那一半):稀疏自生信号绑不住已冻结的读出,只有真值上的稠密梯度行

**这是什么墙。** 两条主张。(1) 文化层:有真值锚定时语言才能被维持——POWERED,6 seed,world_only(真自我模仿)0.068 vs social/distill 0.85 [ctm_cultural_verdict.json,verdict=CULTURAL_TRANSMISSION_MAINTAINS,6 seed]。(2) within-life 那一半:中途把 (dir,type)→payoff 排列一下,冻结读出后,稀疏自生学习重新绑不回去——verdict=NO_WITHIN_LIFE_RECOVERY [ctm_wll_rebind_pilot.json]。主张(1)真站住;主张(2)是软肋。

**我们攻过几招、怎么败的。** FROZEN 对照→0.092≈随机(确认 π 真的打断了旧映射);WLL_ON 奖励门控自模仿→0.162;NO_MEMORY→0.162;WLL_REINFORCE(heads-only PG + 均值基线)→0.251(自驱最强,但远低于 0.45 地板/0.91 天花板);WLL_SCOUT_TOO(连 scout+core 一起解冻)→0.251;DISTILL_SWITCH(真值 π 上的稠密梯度)→0.911(真值天花板);precheck(无限监督数据)→0.933 [ctm_wll_precheck_pilot.json] = 目标可达、读出可重绑。失败机理写得很清楚:坍缩策略在 π 下成功率只有 ~16%,模仿 buffer 被饿死——这是教科书级的稀疏奖励问题。

**最该试但没试的一招。** 加一个**稠密但非真值**的自监督信号,同时用探索打破 1/16-每头的成功饥饿:(a) 温度/熵 schedule + count-based/RND 新颖性奖励,让坍缩策略产出正确样本远超现在的 16%;和/或 (b) EM 式自蒸馏——π 是确定性排列、旧映射完整可得、每个 cell 的奖励是稠密的逐 cell 信号,"把每个 content 指派给最常给奖的 cell,再对该指派做稠密 CE",把 16 个稀疏 bandit 变成一个稠密重标注目标。试过的所有 arm 都是 temp=1.0 固定、无探索奖励、无课程、无稠密辅助目标的单步稀疏 RL。墙自己的论点("只有真值上的稠密梯度行")恰恰就是"稠密-非真值"这条 arm 会去反驳的命题,而这条 arm 结构性地缺席。

**裁决:PREMATURE_THEOREM。** 文化那一半真封死了、且 powered。但命名这堵墙的 within-life 那一半是 prose 把一个 **2-seed pilot** 升级成了定理:ctm_wll_rebind_pilot.json 的 block="pilot"、seeds=[0,1],**根本不存在 ctm_wll_rebind_verdict.json**;而 CTM_ARC_WRITEUP.md:72-79 直接把它当定论写。这低于本实验室自己的 ≥6-seed 红线。失败机理明说是信号**稠密度**问题而非不可能(precheck 0.93 证明容量在),却没跑过任何稠密-非真值 arm 就宣布"只有真值上的稠密梯度行"——这是把结论当前提。注意:这堵墙引用的强结论(可微通道里的梯度 > 稀疏 RL)在这里**反着切**:它说明绑定约束是梯度稠密度,而稠密-非真值梯度是可构造的。**(breakability 6.5)**

---

## 墙 2 ·COMPOSITIONALITY WALL:多属性 JOINT held-out 泛化长不出来

**这是什么墙。** 主张:from-scratch referential-game 家族里,完整多属性组合语言长不出来(held-out JOINT 一直是 0),只有手工硬塞的逐属性分区才行。Prose 宣称"沿三条轴全部 CLOSED + SCOPED THEOREM"(CTM_ARC_WRITEUP.md:139-152)。**但机器裁决不同意**:ctm_compwall_verdict.json=INCONCLUSIVE,ctm_brainaxis_verdict.json=INCONCLUSIVE,ctm_openref_verdict.json=DISCRIMINATOR_BROKEN,只有 ctm_openref_suff_verdict.json=APPARATUS_SUFFICIENT(只说装置能用,不是墙被确认)。没有任何 JSON 吐出 CLOSED/THEOREM——这两个词只在 prose 里。

**我们攻过几招、怎么败的(这些是真打)。** 学习压力轴(compwall,5 个属性对称压力:熵平衡/双群体/课程/slot-swap/token-dropout):收敛的 arm held-out primary_joint 全是 0.0,ci=[0,0],topsim 0.20-0.44(holistic)。脑结构轴(brainaxis:MLP、slot-attention K3_SEP0/SEP02、VQ_BETA0/025):收敛脑的 held-out joint 0.0-0.17(4×4 随机 0.0625),最好的 MLP 0.125 但 CI 下界低于随机。Kirby 迭代学习/压缩瓶颈(ctm_gcrl_il):bottleneck_rise=0.0,joint 5 代钉死 0,且现场抓到 attr1/attr2 **反相关**竞争机制。这些是真攻、真败的,split 设计也干净(每个属性值都进训练,held-out 是真新组合)。

**最该试但没试的一招。** 在共享读出上加一个**生长式(非手塞)的解耦目标**:beta-VAE / total-correlation / HSIC 惩罚,或一个可学习的 routing/gating 层,逼有界码的因子统计独立、各自预测一个属性,但**不手工指定哪一片码对哪个属性**。这跟所有跑过的都不同:5 个压力 arm 是对称**通道**正则,slot/VQ 是在输入/codebook 侧加先验,**没有一个**把梯度压力直接加在读出上去做因子化。grep 全 offscreen/*.py 找 beta-vae|disentangl|total-correlation|hsic|factor-vae:run 代码里 **0** 个真 arm(ctm_openref_run.py:424 只有一个叫 `DISENTANGLED_COORDINATE_CODE` 的硬编码 oracle **字符串标签**,不是训练目标)。测过的二分法是"全共享读出 vs 静态手塞分区(被 Firewall-0 禁)",中间整段——网络在因子化 loss 下自己发现的**可学习分区**——被跳过了。另外 prose 用"query-conditioned listener 只是重编码 loss(a1)+loss(a2)"把一个方向论证掉了(CTM_ARC_WRITEUP.md:146-148),**没有任何 run 文件**——是说服自己,不是量出来的。

**裁决:PREMATURE_THEOREM(但墙本身是真的)。** 三条"封死"轴里两条机器裁决是非封死(compwall/brainaxis=INCONCLUSIVE,openref=DISCRIMINATOR_BROKEN);按项目自己的决策规则,brainaxis 之所以 INCONCLUSIVE 正是因为 VQ_BETA025 从未收敛(train_joint 0.33-0.46,heldout=null)——所以更强的 VQ commitment 那格**字面意义上没测过**,而 prose 自己也把"收敛那格 VQ"列为待办(line 161)。这不是"撞墙就走编目录":slot/VQ/双群体/课程/Kirby 压缩瓶颈都真跑了真败了,gcrl_il 现场抓到了竞争机制。所以**墙(这些结构长不出它)是站得住的现实**。过早的是那一跃:从"我们试的每种结构都失败 + 给个机理"跳到"SCOPED THEOREM:它不会生长"。文献里长因子化码最常被引的那一招(读出上的显式解耦/TC loss 或可学习 router)**从未作为 arm 实例化**,而通道轴根本没真测过(是 DISCRIMINATOR_BROKEN,不是 null)。封盘是把机理打扮成了定理。**(breakability 4)**

---

## 墙 3 ·FLOCKING WALL:具身/空间世界奖励"跟邻居"而不是"传内容"

**这是什么墙。** 主张:2D/具身世界奖励扎堆/共位而非有根的消息内容,所以选择从不维持语言;唯一的"活体胜利"(ctm_spatial_content_life)是个全知-斥候→盲眼-觅食者的脚手架。由 ctm_comm_affordance_verdict.json=WORLD_REWARDS_FLOCKING_NOT_COMM 和 ctm_spatial_content_life_verdict.json 的 honest_claim="Spatial content-pressure life; scaffolded language, not spontaneous." 定义。

**我们攻过几招、怎么败的。** 理想手编通讯者(comm_affordance_pilot):open-vs-mute +0.31 但 open-vs-SCRAMBLE 只 +0.17 [0.039,0.27],没过线→FLOCKING。失败原因:说话者靠近食物时自己看得见,信号跟邻近度冗余=扎堆。TFER 具身合作:CHANNEL_NOT_LOAD_BEARING,"具身是装饰"。脚手架 pair-forage/spatial/grid:全部"scaffolded, not spontaneous"——斥候看到**完整**内容(dir+type),觅食者只看到 decoy 随机 obs 或零向量(已核 ctm_pair_forage_run.py:73-76 是 `decoy=torch.randint(...)` 随机 one-hot;ctm_spatial_content_life 觅食者盲眼)。消息纯属转述一个斥候已经完全持有的答案。感知噪声 sweep(perception_noise):MAP_PARTIALLY_DEGRADES,但只是给同一个全知-斥候拓扑加噪声,没有把信息**分散到不同身体**。

**最该试但没试的一招。** **分布式部分感知**:把答案拆到不同身体,谁都不持有完整答案——斥候看到资源**类型**但看不到**位置**,觅食者看到**位置/空间布局**但看不到**类型**,奖励要求**两者都对**(走到对的地方 AND 匹配对的类型)。这跟跑过的 8 种设计都不同:那里斥候永远看到 100% 答案,觅食者 obs 被刻意设成无信息(零向量/随机 decoy)。所以每个"胜利"都是纯解码-答案的转述,每个 flocking 结果之所以成立,是因为说话者的信息**超集**了听者需要的——这正是"跟着说话者的身体走(扎堆/共位)"能替代"解码它的消息"的原因。分布式部分感知在信息论层面消掉这个退化:没有任何一个你能扎堆过去的邻居持有联合答案,共位就替代不了内容,而且听者必须把消息和自己那私有一半**融合**(真双向依赖,不是转述)。团队自己的红队 spec(STAGE_CTM_HYBRID_COMM_SPEC.md:75-76)亲口把"信号能消歧、扎堆不够用的世界"叫作 "the real next fork"——然后只造了内容压力-脚手架那一半,从没造分布式信息那一半。grep 全 run 代码:`tcdol_run.py` 的 "complementary" 是指分工角色,不是互补**感知**;没有任何 run 实现跨身体互补感知。

**裁决:PREMATURE_THEOREM。** FLOCKING 裁决是个机理,解释了**所测的那些世界**为什么奖励扎堆——不是"没有任何具身世界能奖励内容"的证明。在每个测过的世界里说话者感知都是听者所需的超集,这条件下"扎堆胜过内容"几近同义反复。唯一能溶解这个机理的一招(让说话者**看不到**听者那一半:互补不相交观测、奖励需双方)从未跑过。团队自己标记了这个方向,然后退回到一个连自己 honest_claim 都承认"scaffolded, not spontaneous"的感知不对称脚手架。这就是退在最强一招之前。**(breakability 5.5)**

---

## 墙 4 ·BEYOND-COMMUNICATION WALL:合作全都坍缩成"互相解码"

**这是什么墙。** 主张:每个社会/合作任务都坍缩成"互相解码",没有任何真正"超越通讯"的东西涌现。由 lock 家族裁决串定义:two_key_coop=SUCCESS_GROWN_LANGUAGE_ENABLES_COOPERATION(但结构上可约化)、tcdol=DOL_CEILING、rr=ROTATION_CEILING、compose=HARD_REJECT、align=DIVERSITY_ARTIFACT。要害:专门设计来击败约化的 S2 关系双钥锁,联合动作在代数上就是 decode(B) AND decode(A)。

**我们攻过几招、怎么败的。** S2 双钥锁(模 3 秘密 S=(A+B)mod3)精确复现:open(AND)=0.874=p²(单体解码 p≈0.93),coord_x2(OR)=0.994=1-(1-p)²;赢得 SUCCESS 的"pivotality"(lock 0.559 vs coord 0.041)只是两个**独立**解码事件上平凡的 AND-vs-OR 淘汰不对称。而它的 SUCCESS 之所以成立,是把 spec 自己的原始率判别器换掉了——`coord_minus_coop` 在 two_key_coop_verdict.json 里**字面被标记** `deprecated_do_not_use_raw_rate_conjunction_vs_replaceable_control`。TC-DOL:DOL_CEILING,MR_open 减 decode_only = -0.058(在错的一侧排除零)。RR:ROTATION_CEILING,坍缩到 signal-only/memory-only。Neural RR:CAPACITY_HELPS_NOT_ENOUGH,coordination 钉在随机 0.495。COMPOSE:HARD_REJECT。ALIGN:DIVERSITY_ARTIFACT,scrambled null 反而赢。CTM-ALIVE:SURVIVAL_ONLY_NO_SOCIALITY,真实世界里通道载不动东西。

**最该试但没试的一招。** **推 PCGR——它已经砸开过这堵墙一次,然后被半途丢下。** pcgr_coop_verdict.json=SUCCESS_GROWN_LANGUAGE_SUSTAINS_COSTLY_COOPERATION 是唯一一个可证**不是**互相解码的设计:一个有代价的捐赠博弈(cost_real=true),消息携带的是**第三方、绑身份、依历史**的声誉。决定性对照已核实:open late_cooperation **0.975** vs type_broadcast **0.011**(纯类型解码)vs history_shuffled **0.008**(乱序历史的解码)。纯解码器拿 ~随机;只有载声誉的通讯能维持合作。这按项目自己的 DECODE_RELABELED falsifier(pcgr_coop.py:281-284)就是超越互相解码。而它从没被推下去:(1) 选择-维持检验很脆——drift arm late_cooperation=0.66(sd 0.46),open 只是靠"叛逃者偏多"的诊断压过 drift,不是稳压;(2) 这里的声誉是 replicator-基因演化出来的,不是 **within-life 学来的**——没试的一招是**within-life 学习的声誉策略**:让 agent 必须从观察到的第三方互动里**推断该信任谁**(可证不可解码:没有任何消息直接说出答案,agent 必须整合一段历史)。这跟每个 lock 家族任务(全是单步 decode+算术)以及 S2 的构造性约化都**范畴不同**,因为不可约对象是一个**时间上被整合的社会推断**,不是一次性符号读取。

**裁决:RETREATED_EARLY。** 这堵墙对 lock 家族(S2/TC-DOL/RR/COMPOSE/ALIGN)是**真的**——我攻了专门设计来击败约化的 S2,它站住了:open=p²、coord_x2=1-(1-p)² 精确复现,"合作"就是 decode(B) AND decode(A);其 SUCCESS 只靠把 spec 自己的原始率判别器(现已被标 deprecated)换成微分 pivotality 才活下来。诚实之处:canonical writeup 并没把 two_key 当胜利来存,这其实是默认了约化。**但**这堵墙的全称主张("没有任何超越通讯的东西涌现")是**假的**,而且退却是真的:PCGR 用碾压解码对照的、生长式声誉维持了有代价合作。它砸开过墙一次,然后卡在脆弱的 drift 边际和一个崩掉的种子上,从没升级到那个明摆着的下一招(within-life 学来的、时间整合的声誉推断)。**(breakability 6.5)**

---

## 墙 5 ·DENSE-NON-TRUTH-SIGNAL WALL:自监督预测 = "洗过的真值"

**这是什么墙。** 主张:"稠密 + 有根 + 非真值"这个学习信号象限按构造为空——自监督的下一观测预测只是真值的有损代理,所以当不了真正"有根但非真值"的信号。唯一证据是 wm_first_run_verdict.json 里的去噪探针:referent_comp_1 value_added_over_input = **-0.311**,comp_2 = **-0.177**(WM 隐表比原始 obs 更**差**地恢复真 referent)。注意:repo 从没把这写成封盘 verdict 串——wm_first_run 的 honest_summary 只中性地报"true_distance denoising NOW measured";"象限为空/洗过的真值"这个定理是 orchestrator 的综合,**不是机器裁决**。

**我们攻过几招、怎么败的。** 在 A2_fitness arm(规模化:136 lineage、5152 行、150 repr step)上做了**一个**去噪探针:两个可恢复成分 value_added 都为负(-0.311、-0.177)。解码器是真训过的(decoder 8.25→0.25,kl_dyn 31.2→1.03),所以负结果不是欠训练 artifact——这是唯一真正承重的对照。选择性检验(shuffle 对照)仍正(+0.138、+0.114),隐表确实载真信号,只是赢不过原始通道。

**最该试但没试的一招。** 把**同一个去噪探针**改跑在**有噪声的通道 arm**(--arm A_scramble;systems/live_social_world.py:74 把 A_scramble 映射到 channel_mode 'scramble' 真排列病变),而不是 A2_fitness——后者是 channel_mode 'open'=**无病变**=干净通道=去噪空间为零。这跟跑过的都不同(不是换 size/seed 重放):现有每个去噪裁决都跑在干净 'open' 通道上,那里原始 input_acc 已饱和到 0.95-0.97(wm_first_run comp_1 in=0.966,comp_2 in=0.948)——对一个本就近完美的基线,你数学上不可能展示"去噪带来的增益"。墙的整个前提("自监督恢复真值不能比原始输入更好")恰恰是在"原始输入 = 真值"的那个唯一 regime 里测的。harness 已支持(wm_first_run.py:121 直接吃 --arm),一行旗标的事。**决定性的是:同一探针、同一 arm 在小规模上已经产出过正结果,而 prose 无视了它**——wm_smoke2_verdict.json comp_1 latent_acc=**1.000** vs input_acc=**0.617** → value_added=**+0.383**(基线没饱和时隐表碾压输入)。JSON 与"洗过的真值"prose 直接矛盾;按 JSON-为准规则,这堵墙的陈述已被 repo 内的一个 verdict 自我证伪。

**裁决:RETREATED_EARLY。** 这堵墙来自**一个** config(wm_first_run,A2_fitness='open'/干净通道),被推广成一个 repo 根本没写下来的"象限按构造为空"定理。三个文件级事实砸它:(1) 混淆——A2_fitness 是 channel_mode 'open',_lesion_message 是 no-op,原始输入已在 0.96 恢复真 referent,对 ~0.96 基线的负 value_added 近乎同义反复,根本没噪声可去;(2) repo 内矛盾裁决——wm_smoke2(同探针同 arm)在基线不饱和时 value_added=+0.383,结果的符号是基线饱和度的函数,不是定律;(3) 那个能区分的实验(有噪声 --arm A_scramble,会压低 input_acc 造出真去噪空间)对去噪探针**从没跑过**。最可能砸破墙的一招唾手可得却没试。**(breakability 7.5)**

---

## 正面回答你的指控:哪些墙我们退早了

按是否真打过分两堆:

**真打过、真站住的(没退):**
- **文化传递(墙 1 的文化那一半)**:6 seed、powered、红队过,world_only 0.068 vs social 0.85。这一半是真封死。
- **lock 家族(墙 4 的 S2 等)**:S2 是专门造来击败约化的,我把它的代数摊开了——确实就是 decode AND decode。这堵子墙是真现实。
- **组合性墙本身(墙 2 的"这些结构长不出它")**:slot/VQ/双群体/课程/Kirby 压缩都真跑真败,gcrl 抓到竞争机制。墙是真的——过早的只是"定理"那一跃。

**退早了的(撞墙就走 / 定理下早了):**
1. **墙 5(DENSE-NON-TRUTH,breakability 7.5)**——最该回去打的。整个定理建在一个**饱和基线**的单一 config 上,而 repo 里已经躺着一个反例(wm_smoke2 +0.383)。区分性实验(A_scramble 通道)一行旗标,没跑。这是最干净的"撞墙就走"。
2. **墙 1 within-life 那一半(breakability 6.5)**——把一个 **2-seed pilot** 当定理写进 writeup,连 _verdict.json 都没有,且明知失败是稀疏度问题(precheck 0.93 证明可达)却没跑任何稠密-非真值/探索/课程 arm。
3. **墙 4 整体的全称主张(breakability 6.5)**——"没有任何超越通讯的东西涌现"是假的;PCGR 已经砸开过一次,卡在脆弱 drift 边际就停了,没升级到 within-life 声誉推断。
4. **墙 3(FLOCKING,breakability 5.5)**——团队亲手把"分布式部分感知/可消歧世界"标成 "the real next fork"(hybrid spec:75-76),然后退回脚手架,那一招从没建。
5. **墙 2 的"三轴 CLOSED + SCOPED THEOREM"(breakability 4)**——两条轴机器裁决是 INCONCLUSIVE/DISCRIMINATOR_BROKEN,VQ 强格没收敛(没测),读出上的解耦/TC loss 这条最该试的 arm 从没实例化。墙本身真,封盘过早。

一句话:**墙大多是真的,但"封死/定理"的标签下早了——尤其墙 5 和墙 1,是把单 config / 2-seed pilot 当成了不可能性证明。**

---

## 该回去打的攻击计划(按 breakability 排序,每招带前置 falsifier)

**1. 墙 5 — DENSE-NON-TRUTH(7.5)。** 一行旗标先验证,再谈定理。
- **攻击**:把现有去噪探针原样跑在 `--arm A_scramble`(噪声通道,会压低 input_acc 造出真去噪空间);如有余力再扫几个噪声档,画 value_added vs input_acc 基线饱和度的曲线。
- **前置 falsifier**:若在 input_acc≤0.7 的噪声 regime 下,隐表 value_added_over_input 的 95% CI 上界仍 ≤0(选择性对照在场),则"洗过的真值"成立,墙真封。否则(预期会像 wm_smoke2 那样转正)定理证伪。

**2. 墙 1 — within-life 绑定(6.5)。** 先补功率,再上稠密-非真值 arm。
- **攻击**:(a) 把 rebind pilot 升到 ≥6 seed 出 _verdict.json;(b) 加 EM 式自蒸馏 arm(用每-cell 奖励把 content 重指派到最常给奖的 cell,再做稠密 CE)+ count-based/RND 探索打破 16% 成功饥饿。
- **前置 falsifier**:若 6-seed 下稠密-非真值 arm 的 post_pi 95% CI 上界仍 <0.45(地板),则"只有真值稠密梯度行"成立。否则定理倒。

**3. 墙 4 — BEYOND-COMMUNICATION(6.5)。** 推 PCGR 到 within-life。
- **攻击**:在 PCGR 上换成 **within-life 学习的声誉策略**——agent 必须从观察到的第三方互动整合历史来推断信任对象(无单一消息含答案);同时把 selection-maintenance 加固到稳压 open>drift(查清 seed-3 崩盘)。
- **前置 falsifier**:若把历史/声誉打乱后(history_shuffled 类对照)合作不掉到 ~随机,说明 agent 没在做时间整合推断、退化回解码,则墙对这招也成立。否则=真·超越互相解码。

**4. 墙 3 — FLOCKING(5.5)。** 建那个被标成 "real next fork" 却没建的世界。
- **攻击**:**分布式部分感知**——斥候见类型不见位置,觅食者见位置不见类型,奖励需双方;明确做成跨身体互补不相交观测(现 run 代码全无)。
- **前置 falsifier**:若 open-vs-SCRAMBLE 的 95% CI 下界仍 ≤0.05(消息内容仍非承重,扎堆仍够用),则 FLOCKING 在信息分散后**依然**成立,墙真封。否则机理被溶解。

**5. 墙 2 — COMPOSITIONALITY(4)。** 最难,但有一招明确没试。
- **攻击**:在共享读出上加**生长式解耦目标**(beta-VAE/TC/HSIC 惩罚或可学习 router),让网络自己发现分区而非手塞;附带先把 VQ_BETA025 强格收敛掉,把 brainaxis 从 INCONCLUSIVE 钉成 BRAIN_AXIS_NULL。
- **前置 falsifier**:若解耦 arm 在 train_joint≥0.95 收敛后,held-out primary_joint 的 95% CI 上界仍 ≤ 随机(4×4=0.0625),且非组合控制任务上不崩,则"对称压力供不出因子分离"的定理在这一招下也成立,可以正式封。否则定理破。

---

# 攻击日志(ATTACK LOG)

## 墙 5 — DENSE-NON-TRUTH:已攻,**HOLDS(攻击失败,干净)**。2026-06-27

按攻击计划第 1 招,在噪声通道 `--arm A_scramble` 上重跑去噪探针,6 seed。**初看像赢,红队 + 决定性对照证明是假象。**

**证据链(全部多 seed、CI、自检通过):**
- 初步:A_scramble 下训练 WM 的 value_added(vs 单帧整数输入)comp_1 +0.109 [0.047,0.171]、comp_2 +0.099 [0.027,0.171],6/6 正;clean arm A2 复现 −0.21 原始负值。**看似定理倒了。**
- 红队的"无聊解释"怀疑者跑了缺失对照:一个**未训练随机 reservoir(同架构)**在 seed0 上 value_added +0.215/+0.159 = 训练 WM 的 3–4 倍,且直接压过训练 WM ~0.17;线性平滑(running-mean/EWMA)做不到 → 是**任何循环网的非线性时间整合**,非"学到的世界模型"。
- 我自己把决定性对照在全 6 seed 干净重跑(`wall5_reservoir_control_verdict.json`,自检 input 重算对上已存数 ±0.000):
  - **训练 WM − 随机 reservoir**:comp_1 **−0.133 [−0.242,−0.024]**,comp_2 **−0.095 [−0.161,−0.029]**,6/6 负,CI 干净 < 0 → **WM 训练反而不如随机网**。
  - **训练 WM − 公平 one-hot 输入**:comp_1 +0.009 [−0.101,+0.119]、comp_2 −0.014 [−0.102,+0.075],**跨 0 = 零优势**。

**裁决:WALL5_HOLDS —— 但 SCOPED,不是 CLOSED。** as-specified 的攻击失败了(那个 +0.10 是"时间整合循环网 vs 单帧弱基线"的双重假象);在这个薄/死世界里 holds。更深的真发现:**WM 的自监督训练在这个薄/死世界(0 capture、comp_0 恒定、信息不丢噪声)里没长出超过随机 reservoir 的有根表示**(= "WM trains but no monitoring win" 的又一实锤)。**两个未钉的洞 → 墙 5 是 PARKED 不是 CLOSED:** (1) "信息真丢"的噪声没测(逻辑上近乎必然仍 holds,但严格说没跑);(2) **致命的:WM 只有在"有真动力学可学"的世界才可能赢过 reservoir(reservoir 学不了动力学)——死世界里测不出梦想要的答案。所以墙 5 的"梦版本"(自监督在有动力学的富世界里能否长出有根理解)只能在富世界里测 → 墙 5 与墙 3 纠缠,搬到富世界那一关再答。**

**未测的最强版(留作记录,不急着追)**:信息**真丢**的噪声(mute / iid 随机替换)下,训练 WM 是否仍 > 最佳输入基线——但既然训练 WM 连随机网都打不过,继续追这堵墙 ROI 低。

**方法论收获(比墙本身值钱):** 任何"墙倒了"的主张,必须带 **architecture-matched null(随机同构网)+ 公平编码/时间匹配基线**,否则不算数。差点 bank 的假赢被这条拦下。所有后续攻墙沿用此模板。

**对 breakability 估计的更新**:墙 5 估的是最高赔率 7.5,结果 HOLDS → 裁决书的 breakability 系统性偏乐观,其余墙(4=6.5、1=6.5、3=5.5、2=4)的预期相应调低。

## 墙 4 — BEYOND-COMMUNICATION:已攻 #1,**INCOMPLETE(选择关没过)**。2026-06-28

按攻击计划,加固 PCGR(`offscreen/pcgr_wall4_firm.py` → `pcgr_wall4_firm_verdict.json`,6 seed,全部臂 + 架构匹配 null,标准初始化 + CI-干净的更严标准)。
- **干净成立(每 seed)**:open 0.975 ≫ mute 0.010 / history_shuffled 0.008 / type_broadcast 0.011 / static_rep 0.011(差 ~0.96,CI 干净)→ **绑历史/身份的真实声誉**内容**是承重的**(子结论,真)。
- **没过的关**:`open − drift = +0.314,CI[−0.03,0.66] 跨 0` → **选择关 FAIL**。drift(随机选择)是**双稳态**,6 seed 里 4 个也锁到 ~1.0 合作 → "声誉**通过选择**维持超越解码的合作"在标准初始化下**立不住**。架构匹配 null(untrained_open)aggregate 被打赢(+0.800)但 seed3=0.988 被双稳态污染;scramble 双峰(0.337,固定排列非纯噪声 = 确认的 confound)。
- **根因诊断**:捐赠博弈锁死在 全合作/全背叛 两吸引子之一,落点由早期随机漂移定、常与语言无关 → 连 drift/scramble 有时都到 1.0。原 PCGR "SUCCESS" 是靠**defector-heavy 诊断初始化**才过选择关;标准初始化下脆点暴露。
- **裁决:WALL4_NOT_FIRMED(attack #1)。** 子结论"声誉内容承重"真;headline"选择维持的超越解码合作"未过 clean 标准。需更多试错:defector-heavy 跑全臂 + scramble 改信息-毁坏型 + 处理双稳态。
- **总账(当时)**:墙 5、墙 4 两次攻击,0 次干净突破,两次都被诚实诊断(墙5假赢被拆/墙4选择被双稳态拆)= 真·试错破墙,不是一击即中。反方"墙4是大概率真赢"亦被证伪。

## 墙 1 — WITHIN-LIFE 绑定:已攻(Codex),**SCOPED BREAK(红队确认,窄范围)**。2026-06-28

Codex 跑 `offscreen/ctm_wll_attack.py`(6 seed,summary `ctm_wll_attack_summary.json`),Claude 验代码 + 红队(`wktkp5ulp`,4 怀疑者全判 kills=false)。
- **真破(存在性证明,banked 在窄范围)**:一个**自生、非真值**信号(agent 自己采样动作的**二值精确匹配奖励** `_env_reward = ((ad==rd)&(at==rt))`;perm 只进奖励+评测,从不当 CE 标签,除了围起来的 DISTILL oracle)把**冻结读出**重绑到中途 payoff 排列 π,到达同跑 oracle 天花板(EM 0.916 / TEMP 0.913 ≤ same-run DISTILL 0.917;6 seed,CI 下界 0.863 > 0.45 floor)。**不是墙-5 式假赢**:杀死墙 5 的那个架构匹配 null(EXPLORE_ONLY_NO_REWARD = 同 temp=8 探索 + 同只训头,但标签忽略奖励)**在场且停在随机 0.085** → 是**奖励内容**承重,不是探索/容量。学习是渐进的(known_cells 一格一格涨、恢复同步跟随),非第0轮灌入 → 无 oracle 泄漏。
- **没证明的(范围卡死)**:① **NCELL=16(4×4)在该预算下可穷举**(visit_counts_min ~654-694)→ 奖励信息上 ≈ oracle(对完整奖励表 argmax = π by construction);**所以这是"穷举发现",不是稀疏信用分配**;EM 落在 DISTILL 0.001 内是意料之中。② **温度混淆**:旧失败 pilot 用 temp=1.0(0.16/0.25),新臂 temp=8.0 + EM 加密集化,**没有任何臂单独隔离温度**,0.16→0.91 跳变归因不清。③ 无样本效率差、无泛化(16 点)、无超越精确匹配 argmax 的信用分配、无 scaling 路径。
- **裁决:WALL1_WITHINLIFE_BROKEN_SCOPED。** banked claim = "**在可穷举的小空间(NCELL=16),自生奖励能把冻结读出头重绑到 π、到 oracle 上限、对照干净**" —— **绝不升级为"稀疏自信号突破了优化器墙"**(深层那半未动)。
- **决定性后续(决定它是真能力还是小空间穷举)= NCELL-scaling null**:NCELL∈{16,64,256},**固定每格预算**(explore_n×rounds/NCELL 恒定),再加固定总预算版。穷举假说预测 post_pi 随 NCELL 增大塌向随机、且开出"低于同跑 DISTILL"的差;真能力则优雅退化。+ 温度单独消融 + coverage-matched 稀疏臂(每格只留 k=1 成功、关掉 argmax 加密集化)。
- **更新总账**:墙 5 没破(假赢)| 墙 1 = **第一个红队确认的破,但 SCOPED**(存在性证明,深层未动,待 NCELL-scaling 定性) | 墙 4 provisional firm,红队复核中。**攻墙机器在双向工作:既不橡皮图章(墙5杀)、也不虚无否定(墙1确认+卡范围)。**

### 墙 1 — NCELL-scaling 后续完成(Codex,分支 `codex/wll-scope-redteam` commit `e7b9fcd`;Claude spot-check 数字全对)。2026-06-28
**最终裁断:`REAL_BUT_COVERAGE_LIMITED_TABLE_DISCOVERY`。** Codex 自己设计了判别(没盲跑 N16):温度消融 + 两种预算制度 + k=1 对照。
- **温度消融解决了温度混淆**:T1=0.149(null,不过 floor)、T2=0.373(部分)、T4=0.809、T8=0.913 → **当初 NO_WITHIN_LIFE_RECOVERY 主要是低温(temp=1)探索饥饿的假象**,不是不可能。
- **覆盖悬崖确认(决定性)**:post_pi 跟的是 **successes_per_cell / coverage**,不是 NCELL 本身。N256 **固定总预算** → 0.151(coverage 0.155,~0.2 成功/格)**塌到随机**;N256 **固定每格预算** → 0.932(coverage 0.94,7.4 成功/格)**照样到顶**。
- **k=1 ≡ EM**:每格只留 1 次成功 = 完整 reward-table argmax,说明"密集化"不是额外魔法,**核心是"每格至少发现一次正确动作"**。
- 纪律全程在场:explore-only-no-reward 始终不重绑;同跑 DISTILL 始终是 oracle 上限;π 只进奖励/评测。
- **诚实含义:within-life 的"优化器墙"其实是一堵"覆盖墙"。** 一旦覆盖够,dense-CE-on-discovered-labels 就能重绑;大空间固定预算下覆盖不到就塌。**瓶颈是探索/覆盖,不是绑定本身。**
- **banked(窄)**:"覆盖充分时(小空间 OR 足够每格预算),自生奖励能重绑冻结读出到 oracle 上限"。**未 bank**:大空间固定预算下的重绑、深层非表格 credit assignment、自然生命周期里的自发重绑。
- **真前沿(Codex 下一步候选)= 主动/奖励导向探索**(在大空间里不靠穷举也能覆盖),保持同样 no-reward null。
- **总账更新**:墙 5 没破 | **墙 1 = 真破但"覆盖墙"刻画清楚(优化器墙被精确改写,不是推倒也不是假赢)** | 墙 4 红队复核中。

## 墙 4 — attempt #2 红队(`w6b2j3toz`)裁决:**INCONCLUSIVE_NEEDS_CONTROL(没 firm)**。2026-06-28
红队一分为二(4 怀疑者,robustness 判 KILL sev8,但其 8-seed 重跑无磁盘产物=未核实;另三刀核实,单凭它们已足够 INCONCLUSIVE):
- **真站住(banked 子结论)**:defector-heavy 下,长出来的共享声誉**内容承重** —— open 干净压过 architecture-matched untrained-null + mute/history_shuffled/type_broadcast/static_rep,CI 全干净,mii 0.855,决策路径无 true_bin 泄漏(choose_act = give iff rep_hat≥g_thr;energy = 捐赠 payoff + walk cost)。**杀死墙 5 的那个 null,这次过了。** = 间接互惠 image-scoring 经由长出来的通道,内容确实承重。
- **没站住(headline 死)**:① "选择维持(open>drift)"只在唯一那个 defector-heavy init(0.20/0.05/0.75)CI 干净;标准 init = attack#1 NOT_FIRMED。② **那个失败的标准门在冻结 commit `8ee018c` 里被从 blocking 改名成 `diagnostic_` 非阻断 = 动了冻结预注册**(违反铁律,红队在 git 历史抓到)。③ clean +0.469 靠 6 个未配对、双峰种子(5/6 落合作吸引子,seed0 崩,mii 最低 0.734)= basin 抽奖,非稳定选择效应。④ WALL4_FIRMED 只在未跟踪文件、跟已提交 WALLS_VERDICT.md(NOT_FIRMED)打架。⑤ scope 超界:认知是无状态遗传阈值(无在生学习/无互惠记账/无 ToM)→ **确认"合作 = 可读声誉 + 阈值 + 选择"的还原论读法,不是"超越通讯"**。
- **裁决:WALL4 = INCONCLUSIVE。** banked 仅 = "长出来的声誉内容承重(超越降级解码 + 超越 null)";**不 bank** "选择维持""超越通讯"。**决定性后续 = 预注册的 init-BAND sweep(open vs drift 跨一整条叛逃压力 init,≥6 seed,配对 RNG)+ ≥20 seed 报 basin-escape-rate 为主端点**;只有一整条 band 都 open>drift CI 干净,选择腿才算 firm。
- **治理教训**:原 PCGR "Path 2 SUCCESS"(commit `8ee018c`)本身就把失败门软化成 diagnostic 了 → **原结论也被这次审计削弱**,不止 attempt#2。

---

# 红队后总账(全部复核过,2026-06-28)
**0 堵墙干净突破。**
- **墙 5**:没破(假赢=时间整合工件,被随机 reservoir 拆)。
- **墙 1**:**真破但 SCOPED** —— within-life 优化器墙 = 一堵"覆盖墙";自奖励能重绑(覆盖够时)、甚至泛化到没见过的格(**但要"结构 + 装上的匹配 bias"同时在场**;随机 π 或 table 模型就塌)。深层"长出结构"未动。
- **墙 4**:**INCONCLUSIVE** —— 声誉内容承重(子结论真),但"选择维持/超越通讯"没 firm(basin 抽奖 + 单 init + 改门)。
- **反复浮出的同一堵真墙 = 装上去的结构能用,长出来/发现出来的结构才是没攻下的前沿**(墙2=正面攻这个;墙1深层、墙5 都汇到这)。
- **攻墙机器在双向工作,且抓住了我自己两次过度乐观(墙5假赢、墙4 headline)**——这正是"撞墙就走/虚报赢"的解药。

## 墙 2 — 已攻(Mac,分支 `wall2-mac`;Claude spot-check 通过)。2026-06-28
Mac 做了 WALLS_VERDICT 点名"中间整段被跳过"的那招 = **读出侧生长式解耦家族**,4 种结构性不同的实现:
- **V1 VICREG_LATENT**(32d sync cov-decorr):held 0,omm **−0.106** → NULL(latent 太宽、4 ref 平凡可分,penalty 反伤 token)。
- **V2 VICREG_BOTTLENECK**(K=6 / scale4 K=8):held 0 → NULL(**VICReg 当优化器加速器,不当 disentangler**;head 仍学一个 holistic 范畴)。
- **V3 ROUTER_DISJOINT**(per-position sigmoid mask + overlap penalty):train 卡 0.84 → NULL(overlap 拦住了 holistic,但 latent 没保证含正确 attr,卡在两不靠)。
- **V4 PAIRED_FULL**(VICReg + Router 合):held 0,omm **−0.25**(比闭嘴还差,自毒)→ NULL。
- 对照全过(SHARED_BASE arch-null 平、SHUFFLE_PENALTY_NULL 平);no-oracle 沿用 compwall。
- **家族级 verdict**:读出侧生长式解耦(latent 几何 / bottleneck / head 结构分区 / paired)**全 NULL,且既收敛又 held=0** → 给原 INCONCLUSIVE **加 4 个真 null,墙 2 更紧**(与 Locatello 无监督解耦近乎不可能一致)。
- **Mac 的关键自陈洞见**:scale 3/4 太小,4-7 ref 用 vocab=5 msg=2 编 holistic 太容易 → 任何"让 holistic 难"的压力只会让模型卡住不收敛。**"不是脑的问题,是世界太小。"** (powered scale-5 未跑,GPU 4.8h,留台式机。)
- **V5/V6 续(Mac,branch `wall2-mac` `6bb8d6b`;Claude spot-check 通过)→ 根因定位**:V5(speaker 硬分区,listener 不动)NULL;V6(3 阶段课程+冻结)NULL,但 **force-eval 测 P1+P2 后 held=0 且 held-out 上 open==mute**。**铁证:消息本身在没见过的组合上不带信息 → 瓶颈是 SPEAKER(消息生成),不是 readout。** 根因 = speaker CTM 核心只在 4 个训练组合上训过 → 对没见过的输入组合 OOD → emit 非语法乱码,读出端再强也白搭。**所有 readout 侧攻击(V1-V6)治错地方;墙 2 的根在 input 侧(说话者输入侧组合泛化)。更深:compwall 的 attr1/attr2 完全对称 → 世界不给"该分开"的信号 → 对称脑 fix 被对称世界拉回 holistic。** = 大汇合"瓶颈在世界"的机制级实锤,且正面验证 RTC(非对称、世界提供分离信号)的方向。**墙 2 readout-attack 章节关闭(6 攻击 + 根因)。下一步 = "改 task 不对称"的便宜测试 = RTC 核心 premise 的去风险(asymmetric 世界能否让 grown JOINT 涌现;null 则 RTC 的 G1 JOINT 探针大概率也 null,投建前就知道)。**

---

# 大汇合(GRAND CONVERGENCE,2026-06-28,红队后)
**3 个 agent、5 堵墙、多轮红队 → 0 堵干净突破,但收敛到一个一致的诊断:**

**每堵墙都败给了"薄/小世界"允许的一条捷径:**
| 墙 | 捷径 | 世界为什么允许它 |
|---|---|---|
| 墙 5 | 时间整合(随机 reservoir 就够) | 感知太薄、世界太死(0 capture),WM 无东西可学 |
| 墙 1 | 暴力覆盖 / 装上的结构 | 空间小到能穷举;或结构是手装的 |
| 墙 4 | basin 抽奖 | 种群太小(pop=24),合作不是吸引子是运气 |
| 墙 2 | holistic 编码 | 任务太小,holistic 太容易,组合压力一上就卡住 |

**两条收敛结论(其实是一枚硬币的两面):**
1. **瓶颈是世界,不是脑/优化器。**(墙 1/2/4/5 四堵、3 个独立 agent + 红队各自撞到。**这次是"挣来的"诊断,不是断言。**)
2. **结构在"太小到不需要它"的世界里长不出来;装上去的结构能用。**(墙1-DoorB 装 factorization 能泛化、墙2 生长式解耦全 NULL、墙5 同理。Locatello 味。)

**→ 挣来的前沿(回答整场"往哪走"):造一个"捷径会失效"的更丰富世界。** 这场攻墙等于**反推出了富世界的设计 spec**——它必须让每条捷径都死:
- 组合压力丰富到 holistic 编不下(杀墙2捷径);
- 空间大到不能穷举、但有可学结构(杀墙1捷径);
- 种群/动力学丰富到合作是吸引子不是抽奖(杀墙4捷径);
- 感知丰富到必须预测/建模(杀墙5捷径);
- **分布式部分感知**(墙3 从没试过的那招)杀 flocking 捷径。
**诚实**:"造富世界"是 flocking 坟场,我们失败过很多次;但**现在第一次有了一份从"每条捷径"反推出来的精确 spec**,这是新的。

---

# RTC 建设日志

## MVP-0 / G0 世界有效性(Codex,branch `codex/rtc-mvp0` `0a08a05`;Claude 核代码)。2026-06-28
Codex 报 `RTC_G0_WORLD_VALID`,我核了 `rtc_g0_run.py`:
- **真·干净**:reservoir/clock_only/solo-no-fusion 6/6 全死(alive 0.0);clock 预测隐藏场 max R2 **0.0291<0.03**(24 个 seed×channel 里 23 个≈0)→ 无捷径可活、时钟预测不了场。**MVP-1 需要的前提("生存必须拿到缺失通道信息 → 消息/融合会承重")成立。**
- **两处过度声称(我点破,Codex 须纠正)**:① "forecaster 正控=世界可学"**实为 oracle**——它读 `world.patch()`(真实场全 4 通道),不走合法感知(`perceive` 返回被丢弃);只证明"有全信息能活",不证明"合法感知能学会"。② **差别进食门**(forecaster θ−0.05 / solo θ+0.15 / reservoir·clock 不能歇)= 规则不对等 confound。
- **裁决:G0 方向有效,可进 MVP-1**(必要性前提稳,且 reservoir 用随机权重即便给公平规则也会死);**但要求**:forecaster 诚实改标为 fenced-oracle 可解性上限(非 learnability)+ 消除/承认差别门 + **真正的"合法感知可学性"留到 MVP-2 的 G2(WM vs reservoir,绝不用 oracle)**。

## 墙 2 — compwall 章节收尾(Mac,V1-V8,branch `wall2-mac`)。2026-06-28
**8 轮结构性不同的攻击全 NULL → 墙 2 在 compwall scale=3/4 是站得住的实墙。** 6 脑侧(V1 VICREG_LATENT/V2 VICREG_BOTTLENECK/V3 ROUTER_DISJOINT/V4 PAIRED/V5 GRAD_ISO/V6 PHASED_CURRICULUM)+ 2 世界侧(V7 HEAD_DROPOUT 损失不对称/V8 BLOCKED_ATTR2 时间尺度不对称=did_not_converge)。共同模式:shared CTM core 不变 → 永远 holistic。
- **两层定位**:SPEAKER 编码器=真墙(7 轮堵死,根因=输入侧组合泛化);LISTENER=装好分离后有潜力(INSTALLED_SPLIT 天花板 23%→30% scale3→4,容量受限;**注:scale4 "WIN" 是 5/6 seed + 装的,记为"装好的组合容量随 scale 涨",非墙2被破**)。
- **三重印证**:8 实验 + Gemini 文献(Locatello 2019 无监督解耦不可能 / Chaabouni 组合性不免费)+ 跨模型一致。
- **V8 = RTC premise 去风险,失败**(时间尺度非对称没让 grown speaker 涌现 JOINT;弱保留:训练不收敛,非干净 JOINT=0)→ **RTC 的 G1 JOINT 探针大概率也 null**(spec 早写明=可能 ship null 的探针,非承重)。**RTC 仍交付**(S4/S5/S6/S3);"完整组合语言"最硬、这些 scale 上很可能仍开着,RTC 最可能长出"半组合但承重+可传承+撑合作"的语言。**墙2 compwall 章节关闭,问题正式搬进 RTC G1。**

## MVP-1 / G1(Codex,branch `codex/rtc-mvp1` `5203d39`;Claude 核代码)→ **RTC_G1_STOP_FAILED_GATE(未 bank)**。2026-06-28
Codex 正确地 G1 失败即停、没进 MVP-2,且折叠了 3 个 G0 纠正(公平规则下 G0 仍过=差别门 confound 可去、捷径真死)。但我核代码后两点泼冷水:
- **fusion-survival FAIL 的真相 = 谁都活不下来(策略侧/优化器墙,不是通道)**:全部策略 alive=0;solo/mute/body rest_rate=1.0 歇着饿死(age 278),fusion/scramble 会吃但 bad_rate≈0.46/0.58 吃毒死更快。**从零 CTM 策略学不会"靠融合信息求生"(= spec honest_risk #2)**;门测不出通道承重(无 lift 可测)。通道有微弱帮助(fusion 比 scramble 毒少)但远不够过生存线。
- **"GROWN_JOINT_PASS"(0.78-0.92)不是破墙 2,是误标的装好分区**:`rtc_language.py:80-81` 证 `train_relay_channel = FactoredSpeaker + FactoredListener`(装好的逐属性分区);holistic null = 随机查表(seen 外必 ~0)。所以 held-out 泛化 = **装好 factored 架构泛化**(wall-2 早知的基线 + spec §3 "install partition, grow use" 设计;"grown"只指权重训出来、分区是装的)。**墙 2 真墙=共享核长出分区(compwall 8 轮证明不行);FactoredSpeaker 把分区写进架构 → 不算破墙。** 第 3 次攻墙机器抓到误标的"赢"。
- **裁决:MVP-1 G1 失败在行为侧;通道侧(装好的)能载信息但策略学不会用它求生 → 优化器墙在 RTC 行为层重现。** 不 bank、不合 master。
- **下一步 = spec 的 scripted-forage fallback(解耦"策略能不能学" vs "通道承不承重")**:给胜任/脚本策略让生存可达 → 测 open vs mute/scramble/body-follow 的存活 lift(干净测 S5);JOINT probe 诚实改标(装好分区泛化,非 grown);若要测 RTC 里真 wall-2,加共享核(非 Factored)臂(按 compwall 大概率 null)。
