import logging
import os
import sys

logger = logging.getLogger(__name__)

DOCUMENTS = [
    {
        "title": "2型糖尿病诊疗指南（2024版）",
        "content": """【诊断标准】
2型糖尿病的诊断标准如下：
1. 空腹血糖（FPG）≥7.0 mmol/L（126 mg/dL）
2. 口服葡萄糖耐量试验（OGTT）2小时血糖≥11.1 mmol/L（200 mg/dL）
3. 糖化血红蛋白（HbA1c）≥6.5%
4. 随机血糖≥11.1 mmol/L且伴有典型糖尿病症状（多饮、多尿、体重下降）

以上任意一项即可诊断，无症状者需两次检测确认。

【治疗原则】
1. 一线用药：二甲双胍（无禁忌证前提下），起始剂量500mg，每日2次，随餐服用
2. 若HbA1c≥9.0%，可考虑起始联合治疗或胰岛素强化治疗
3. 血糖控制目标：一般成人HbA1c<7.0%；老年或合并症较多者可放宽至<8.0%
4. 血压控制目标：<130/80 mmHg
5. 血脂控制目标：LDL-C<2.6 mmol/L（合并心血管疾病者<1.8 mmol/L）

【并发症筛查】
- 每年至少检查一次眼底（视网膜病变）
- 每年检查尿微量白蛋白/肌酐比值（糖尿病肾病）
- 每年检查足部（糖尿病足筛查）
- 定期检查心电图（心血管并发症）

【生活方式干预】
1. 饮食：控制总热量，碳水化合物占50-60%，优先选择低GI食物
2. 运动：每周≥150分钟中等强度有氧运动，减少久坐时间
3. 体重：BMI≥24的超重患者建议减重5-7%
4. 戒烟限酒""",
        "category": "clinical_guide",
        "source": "中华医学会糖尿病学分会2024年指南"
    },
    {
        "title": "原发性高血压分级管理规范",
        "content": """【血压分级标准】
根据《中国高血压防治指南》，原发性高血压分级如下：
1级高血压（轻度）：收缩压140-159 mmHg 和/或 舒张压90-99 mmHg
2级高血压（中度）：收缩压160-179 mmHg 和/或 舒张压100-109 mmHg
3级高血压（重度）：收缩压≥180 mmHg 和/或 舒张压≥110 mmHg

【危险分层】
低危：1级高血压，无其他危险因素
中危：1-2级高血压，伴1-2个危险因素
高危：1-2级高血压，伴≥3个危险因素或靶器官损害
很高危：3级高血压，或伴临床并发症

危险因素包括：年龄（男>55岁，女>65岁）、吸烟、血脂异常、早发心血管病家族史、肥胖、缺乏运动、高同型半胱氨酸血症。

【降压治疗目标】
1. 一般高血压患者：血压<140/90 mmHg
2. 合并糖尿病、肾病、冠心病者：血压<130/80 mmHg
3. 老年患者（≥65岁）：收缩压<150 mmHg，能耐受者可降至<140 mmHg
4. 脑卒中患者：急性期不急于降压，稳定后逐步降至<140/90 mmHg

【药物选择】
1. 一线药物：ACEI/ARB、CCB、噻嗪类利尿剂、β受体阻滞剂
2. 优先联合用药方案：ACEI/ARB + CCB 或 ACEI/ARB + 利尿剂
3. 不推荐：ACEI与ARB联合使用
4. 特殊人群：糖尿病首选ACEI/ARB，老年人首选CCB，心衰首选ACEI/ARB+利尿剂+β受体阻滞剂

【随访管理】
- 血压达标者：每3个月随访一次
- 血压未达标者：每2-4周调整方案
- 每次随访测量双侧上臂血压，取平均值""",
        "category": "clinical_guide",
        "source": "中国高血压防治指南修订委员会"
    },
    {
        "title": "冠心病患者病历摘要",
        "content": """【基本信息】
患者：男性，56岁，身高170cm，体重78kg，BMI 27.0 kg/m²
职业：办公室职员
就诊日期：2024年12月15日
主诉：反复胸闷气短3个月，加重1周。

【现病史】
3个月前开始出现活动后胸闷、气短，爬2层楼即感不适，休息10分钟可缓解。未予重视。1周前上述症状加重，轻微活动即出现胸闷，伴出汗、恶心，含服硝酸甘油可部分缓解。无晕厥，无夜间阵发性呼吸困难。

【既往史】
高血压病史8年，最高170/100mmHg，规律服用氨氯地平5mg qd，血压控制在140-150/85-90mmHg。2型糖尿病5年，服用二甲双胍500mg bid，空腹血糖7-8 mmol/L。吸烟史30年，约20支/日。父亲60岁患心肌梗死。

【体格检查】
BP 148/92mmHg，HR 78次/分，双肺呼吸音清，未闻及干湿啰音。心界稍向左下扩大，心律齐，各瓣膜区未闻及杂音。双下肢无水肿。

【辅助检查】
1. 心电图：V1-V4导联ST段压低0.1-0.2mV，T波倒置
2. 心脏超声：左室舒张末径55mm，EF 52%，室壁运动欠协调
3. 冠脉造影：前降支（LAD）近段狭窄70%，回旋支（LCX）中段狭窄50%，右冠状动脉（RCA）未见明显狭窄
4. 血脂：TC 5.8mmol/L，LDL-C 3.6mmol/L，HDL-C 0.9mmol/L，TG 2.1mmol/L
5. HbA1c 7.2%，肌酐 98μmol/L

【诊断】
1. 冠状动脉粥样硬化性心脏病 不稳定型心绞痛
2. 高血压病3级（很高危）
3. 2型糖尿病

【治疗方案】
1. 阿司匹林肠溶片 100mg qd（长期）
2. 阿托伐他汀 20mg qn（睡前）
3. 氨氯地平 5mg qd + 培哚普利 4mg qd（联合降压）
4. 美托洛尔缓释片 47.5mg qd（控制心率）
5. 硝酸甘油片 0.5mg 舌下含服 prn（胸闷时）
6. 继续二甲双胍 500mg bid 控制血糖
7. 建议戒烟，低盐低脂饮食，适量运动

【随访计划】
1个月后复查心电图、血脂、肝肾功能，根据结果调整他汀剂量。""",
        "category": "medical_record",
        "source": "北京协和医院心内科"
    },
    {
        "title": "甲状腺结节患者病历摘要",
        "content": """【基本信息】
患者：女性，32岁，身高163cm，体重55kg，BMI 20.7 kg/m²
职业：教师
就诊日期：2025年1月8日
主诉：体检发现甲状腺结节1个月。

【现病史】
1个月前单位体检行甲状腺超声发现双侧甲状腺多发结节，最大者位于右侧叶，大小约1.2×0.8×0.7cm，TI-RADS分类3类（可能良性）。患者无颈部不适、无吞咽困难、无声音嘶哑、无怕热多汗、无体重下降。平素月经规律。

【既往史】
既往体健，否认甲状腺疾病家族史。无颈部放射线暴露史。无药物过敏史。

【体格检查】
甲状腺触诊：右侧叶可触及一枚约1.0cm结节，质韧，表面光滑，边界清楚，活动度好，无压痛。颈部淋巴结未触及肿大。心肺腹查体无异常。

【辅助检查】
1. 甲状腺超声（外院）：右侧叶中下部低回声结节1.2×0.8cm，边界清，形态规则，TI-RADS 3类。左侧叶枚囊性小结节0.4cm。
2. 甲状腺功能（本院）：TSH 2.1 mIU/L（正常），FT4 14.8 pmol/L（正常），FT3 4.2 pmol/L（正常），TPOAb 阴性，TgAb 阴性
3. 血常规、肝肾功能：正常范围

【诊断】
1. 甲状腺结节（双侧），TI-RADS 3类
2. 功能状态：甲状腺功能正常

【处理方案】
1. 目前结节性质倾向于良性，暂不需穿刺活检
2. 建议6个月后复查甲状腺超声，观察结节大小变化
3. 如结节增大超过20%或TI-RADS分类升级，建议细针穿刺活检（FNA）
4. 无需特殊药物治疗
5. 嘱患者注意自我颈部触诊，如有肿块迅速增大及时就诊
6. 保持均衡饮食，适量摄入碘盐，无需忌碘

【注意事项】
甲状腺结节在女性中十分常见，超声检出率高达20-76%。其中约95%为良性，仅约5%为恶性。TI-RADS 3类结节恶性风险<5%，定期随访即可。""",
        "category": "medical_record",
        "source": "北京协和医院内分泌科"
    },
    {
        "title": "二甲双胍临床用药指导",
        "content": """【药品名称】
通用名：盐酸二甲双胍片
英文名：Metformin Hydrochloride Tablets
商品名：格华止、美迪康等

【药理作用】
二甲双胍属于双胍类降糖药，主要通过以下机制降低血糖：
1. 减少肝脏葡萄糖输出（抑制肝糖原异生）
2. 增加外周组织（主要是骨骼肌）对葡萄糖的摄取和利用
3. 延缓肠道对葡萄糖的吸收
4. 改善胰岛素敏感性
二甲双胍单独使用不会引起低血糖。

【适应症】
1. 2型糖尿病的一线治疗用药
2. 与饮食运动控制不佳的2型糖尿病
3. 可与磺脲类、α-糖苷酶抑制剂、DPP-4抑制剂、胰岛素等联合使用
4. 多囊卵巢综合征（超适应症使用，有循证证据）

【用法用量】
1. 起始剂量：500mg，每日2次，随餐或餐后服用
2. 1-2周后根据血糖耐受情况可逐步加量
3. 常用维持剂量：1500-2000mg/日，分2-3次服用
4. 最大剂量：2550mg/日
5. 缓释片：可每日1次，晚餐时服用

【禁忌症】
1. 肾功能不全：eGFR<30 mL/min/1.73m²禁用；eGFR 30-45需减量并密切监测
2. 严重肝功能损害（肝硬化等）
3. 可能组织缺氧的疾病：严重心肺疾病、近期大手术、严重感染
4. 酗酒或酒精中毒
5. 乳酸酸中毒病史
6. 严重维生素B12缺乏（长期使用需监测）

【不良反应】
1. 胃肠道反应（最常见）：恶心、腹泻、腹胀、食欲下降，发生率约20%，多在用药初期出现，随餐服用可减轻
2. 乳酸酸中毒（罕见但严重）：表现为乏力、肌肉酸痛、呼吸困难、嗜睡，一旦怀疑立即停药就医
3. 长期使用可能影响维生素B12吸收，建议定期监测

【注意事项】
1. 使用碘化造影剂检查前后48小时需暂停二甲双胍
2. 手术前需暂停
3. 定期监测肾功能（至少每年一次）
4. 老年患者需评估肾功能后用药""",
        "category": "drug_info",
        "source": "国家药品监督管理局批准说明书"
    },
    {
        "title": "阿莫西林胶囊临床用药说明",
        "content": """【药品名称】
通用名：阿莫西林胶囊
英文名：Amoxicillin Capsules
规格：0.25g/粒、0.5g/粒

【药理作用】
阿莫西林属于β-内酰胺类抗生素中的氨基青霉素，通过抑制细菌细胞壁合成发挥杀菌作用。对多种革兰氏阳性和革兰氏阴性菌均有抗菌活性。口服吸收良好，生物利用度约90%，不受食物影响。

【适应症】
1. 上呼吸道感染：急性咽炎、扁桃体炎、鼻窦炎、中耳炎
2. 下呼吸道感染：急性支气管炎、社区获得性肺炎（轻症）
3. 泌尿生殖系统感染：膀胱炎、尿道炎（非复杂性）
4. 皮肤软组织感染
5. 幽门螺杆菌根除治疗（联合用药方案之一）
6. 莱姆病（早期）

【用法用量】
1. 成人：0.5g，每8小时1次（q8h），或0.75-1g，每12小时1次
2. 儿童：20-40mg/kg/日，分2-3次服用
3. 非复杂性尿路感染：单次3g顿服
4. 幽门螺杆菌：1g bid，联合PPI+克拉霉素+甲硝唑，疗程14天
5. 肾功能不全：eGFR 10-30减量至0.25-0.5g q12h；eGFR<10减至0.25-0.5g q24h

【禁忌症】
1. 青霉素过敏者禁用（用药前必须详细询问过敏史）
2. 有青霉素过敏性休克史者绝对禁用
3. 传染性单核细胞增多症患者禁用（可诱发皮疹）

【不良反应】
1. 过敏反应：皮疹（最常见，发生率3-5%）、荨麻疹、药物热，罕见过敏性休克
2. 胃肠道：恶心、腹泻、呕吐，发生率约5%
3. 肝功能：一过性转氨酶升高
4. 血液系统：罕见白细胞减少、血小板减少
5. 中枢神经系统：大剂量可出现头痛、头晕

【注意事项】
1. 用药前必须进行青霉素皮肤试验（皮试）
2. 有青霉素或头孢菌素过敏史者慎用
3. 与丙磺舒合用可延长阿莫西林半衰期
4. 不宜与别嘌呤醇合用（增加皮疹风险）
5. 疗程一般5-14天，不宜过长
6. 孕妇和哺乳期妇女FDA分类B级，可在权衡利弊后使用""",
        "category": "drug_info",
        "source": "国家药品监督管理局批准说明书"
    },
    {
        "title": "深度学习在肺部CT影像辅助诊断中的应用",
        "content": """【摘要】
目的：探讨基于深度学习的卷积神经网络（CNN）在肺部CT影像中辅助诊断肺结节和早期肺癌的临床应用价值。方法：收集2020-2023年三家三甲医院共12,000例胸部CT扫描数据，其中包含4,500例经病理证实的肺结节患者。采用ResNet-152和DenseNet-121混合架构构建检测模型。结果：模型在独立测试集（2,400例）上达到敏感度92.3%、特异度89.7%、AUC 0.956，对直径≤6mm的微小结节检出率为87.1%。结论：深度学习辅助诊断系统可有效提高放射科医师的阅片效率和诊断准确性。

【引言】
肺癌是全球癌症相关死亡的首要原因，早期发现5年生存率可达80%以上，而晚期发现则不足20%。低剂量螺旋CT（LDCT）筛查是目前公认的有效早期检测手段，但人工阅片工作量巨大，漏诊率约20-30%。人工智能辅助诊断系统的引入有望解决这一临床痛点。

【方法】
1. 数据集：12,000例胸部CT（层厚≤1.5mm），由3位高年资放射科医师双盲标注
2. 标注内容：结节位置、大小、密度（实性/磨玻璃/混合）、形态学特征、恶性概率评估
3. 模型架构：ResNet-152提取全局特征 + DenseNet-121提取局部特征 + 注意力机制融合
4. 数据增强：随机旋转、翻转、缩放、亮度调整
5. 训练策略：5折交叉验证，学习率衰减策略，早停机制

【结果】
测试集2,400例中：
- 整体敏感度：92.3%（95%CI: 91.1-93.5%）
- 整体特异度：89.7%（95%CI: 88.2-91.2%）
- AUC：0.956（95%CI: 0.948-0.964）
- 按结节大小：>10mm敏感度97.2%，6-10mm敏感度93.5%，≤6mm敏感度87.1%
- 按密度：实性结节敏感度94.1%，磨玻璃结节敏感度89.8%，混合密度91.3%
- 诊断时间：AI辅助下平均阅片时间从8.2分钟降至3.5分钟

【讨论】
1. 本模型对微小结节（≤6mm）的检出率有待进一步提高
2. 对磨玻璃结节的假阳性率偏高（12.8%），可能与炎症、纤维化等良性病变混淆
3. 模型在不同厂家CT设备间存在一定的域偏移（domain shift），需进一步优化泛化能力
4. 临床应用中应定位为辅助工具，最终诊断仍需医师确认

【结论】
基于深度学习的肺部CT影像辅助诊断系统具有较高的诊断准确性，可作为放射科医师的有力辅助工具，提高阅片效率，降低漏诊率。未来研究方向包括多模态融合、联邦学习和可解释性AI。

【参考文献】
[1] Esteva A, et al. Dermatologist-level classification of skin cancer with deep neural networks. Nature 2017
[2] Ardila D, et al. End-to-end lung cancer screening with three-dimensional deep learning on low-dose chest CT. Nature Medicine 2019""",
        "category": "research_paper",
        "source": "《中华放射学杂志》2024年第58卷"
    },
    {
        "title": "肠道菌群与2型糖尿病相关性研究综述",
        "content": """【摘要】
2型糖尿病（T2D）的发病率在全球范围内持续上升，肠道菌群作为宿主代谢的重要调节者，在T2D发生发展中的作用日益受到关注。本综述系统总结了近年来肠道菌群与T2D相关性的研究进展，包括菌群失调特征、致病机制及益生菌干预策略。

【肠道菌群失调特征】
多项宏基因组研究一致发现，T2D患者肠道菌群呈现以下特征性改变：
1. 产丁酸菌减少：Faecalibacterium prausnitzii、Roseburia intestinalis等丁酸产生菌丰度显著降低
2. 条件致生菌增加：大肠杆菌（Escherichia coli）、粪肠球菌（Enterococcus faecalis）等丰度升高
3. 菌群多样性下降：Shannon指数和Chao1指数较健康对照显著降低
4. 拟杆菌门/厚壁菌门（F/B）比值改变：多数研究显示T2D患者F/B比值升高
5. 短链脂肪酸（SCFA）代谢通路受损：特别是丁酸合成途径相关基因丰度下降

【致病机制】
1. 肠道屏障功能受损：菌群失调导致肠道通透性增加（"肠漏"），脂多糖（LPS）入血引发慢性低度炎症（代谢性内毒素血症），激活TLR4/NF-κB通路，抑制胰岛素信号转导
2. 短链脂肪酸减少：丁酸是结肠上皮细胞的主要能量来源，同时具有抗炎、调节免疫功能。丁酸减少影响GLP-1分泌，削弱胰岛素敏感性
3. 胆汁酸代谢改变：菌群参与初级胆汁酸向次级胆汁酸的转化。T2D患者胆汁酸谱改变，影响FXR和TGR5受体信号通路
4. 支链氨基酸（BCAA）代谢异常：肠道菌群过度产生BCAA，激活mTORC1信号通路，加重胰岛素抵抗
5. 三甲胺N-氧化物（TMAO）：菌群代谢胆碱/肉碱产生的TMA经肝脏氧化为TMAO，促进动脉粥样硬化，增加T2D心血管并发症风险

【益生菌干预研究】
1. 荟萃分析（2023年，纳入42项RCT，n=3,215）：
   - 益生菌补充显著降低HbA1c（WMD -0.32%, 95%CI: -0.45至-0.19）
   - 显著降低空腹血糖（WMD -0.48 mmol/L, 95%CI: -0.72至-0.24）
   - 显著降低HOMA-IR（WMD -0.52, 95%CI: -0.81至-0.23）
2. 常用益生菌菌株：
   - 双歧杆菌属（Bifidobacterium）：改善糖代谢，降低内毒素水平
   - 乳杆菌属（Lactobacillus）：调节胆汁酸代谢，增强肠道屏障
   - 嗜酸乳杆菌+鼠李糖乳杆菌组合：多项RCT显示可改善胰岛素敏感性
3. 粪菌移植（FMT）：初步研究显示FMT可短暂改善T2D患者的胰岛素敏感性，但长期效果不确定

【未来方向】
1. 精准营养干预：基于个体菌群特征定制饮食方案
2. 工程菌开发：设计能靶向递送治疗分子的活体生物药
3. 菌群标志物：开发基于肠道菌群的T2D早期预测模型
4. 多组学整合：结合宏基因组、代谢组和转录组数据揭示因果关系

【参考文献】
[1] Qin J, et al. A metagenome-wide association study of gut microbiota in type 2 diabetes. Nature 2012
[2] Zhao L, et al. Gut bacteria selectively promoted by dietary fibers alleviate type 2 diabetes. Science 2018
[3] Zhang X, et al. Impact of gut microbiota on the management of type 2 diabetes: a meta-analysis. Lancet Diabetes Endocrinol 2023""",
        "category": "research_paper",
        "source": "《中华内分泌代谢杂志》2024年第40卷"
    }
]


async def seed_database():
    """Check if database is empty and seed with initial data if SEED_DEMO_DATA=true."""
    from sqlalchemy import select
    from app.database import async_session_factory
    from app.models.user import User
    from app.models.document import Document
    from app.utils.auth import get_password_hash
    from app.services.rag_engine import rag_engine
    from app.config import get_settings

    settings = get_settings()

    if not settings.SEED_DEMO_DATA:
        logger.info("SEED_DEMO_DATA is false, skipping seed.")
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.username == "doctor1")
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.info("doctor1 user already exists, skipping seed.")
            return

    logger.info("Database is empty, seeding initial data...")

    async with async_session_factory() as session:
        doctor = User(
            username="doctor1",
            email="doctor1@hospital.com",
            hashed_password=get_password_hash("doctor123"),
            full_name="张医生",
            role="doctor",
            department="全科"
        )
        session.add(doctor)
        await session.commit()
        await session.refresh(doctor)
        logger.info("Created doctor1 user (id=%d)", doctor.id)

        for doc_data in DOCUMENTS:
            doc = Document(
                title=doc_data["title"],
                content=doc_data["content"],
                category=doc_data["category"],
                source=doc_data["source"],
                status="pending",
                chunk_count=0
            )
            session.add(doc)
        await session.commit()

        result = await session.execute(select(Document))
        docs = result.scalars().all()
        logger.info("Created %d documents, starting indexing...", len(docs))

        for doc in docs:
            try:
                chunks = await rag_engine.index_document(doc)
                doc.status = "indexed"
                doc.chunk_count = chunks
                await session.commit()
                logger.info("Indexed: %s -> %d chunks", doc.title[:30], chunks)
            except Exception as e:
                doc.status = "error"
                await session.commit()
                logger.error("Failed to index %s: %s", doc.title[:30], e)

    logger.info("Database seeding complete!")
