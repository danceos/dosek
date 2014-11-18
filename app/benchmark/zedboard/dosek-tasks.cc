
const uint16_t number_of_tasks = 250;
uint16_t pulse_counter_by_task[250];
static volatile int comm_84_to_83;
static volatile int comm_79_to_72;
static volatile int comm_108_to_104;
static volatile int comm_96_to_95;
static volatile int comm_58_to_1;
static volatile int comm_53_to_3;
static volatile int comm_64_to_35;
static volatile int comm_112_to_15;
static volatile int comm_100_to_27;
static volatile int comm_68_to_60;
static volatile int comm_80_to_31;
static volatile int comm_91_to_29;
DeclareTask(T_1_L);
DeclareTask(T_1_H);
DeclareCounter(C_1_hard);
DeclareCounter(C_1_soft);
DeclareAlarm(A_1_hard);
DeclareAlarm(A_1_soft);

DeclareTask(T_2_L);
DeclareTask(T_2_H);
DeclareCounter(C_2_hard);
DeclareCounter(C_2_soft);
DeclareAlarm(A_2_hard);
DeclareAlarm(A_2_soft);

DeclareTask(T_3_L);
DeclareTask(T_3_H);
DeclareCounter(C_3_hard);
DeclareCounter(C_3_soft);
DeclareAlarm(A_3_hard);
DeclareAlarm(A_3_soft);

DeclareTask(T_4_L);
DeclareTask(T_4_H);
DeclareCounter(C_4_hard);
DeclareCounter(C_4_soft);
DeclareAlarm(A_4_hard);
DeclareAlarm(A_4_soft);

DeclareTask(T_5_L);
DeclareTask(T_5_H);
DeclareCounter(C_5_hard);
DeclareCounter(C_5_soft);
DeclareAlarm(A_5_hard);
DeclareAlarm(A_5_soft);

DeclareTask(T_6_L);
DeclareTask(T_6_H);
DeclareCounter(C_6_hard);
DeclareCounter(C_6_soft);
DeclareAlarm(A_6_hard);
DeclareAlarm(A_6_soft);

DeclareTask(T_7_L);
DeclareTask(T_7_H);
DeclareCounter(C_7_hard);
DeclareCounter(C_7_soft);
DeclareAlarm(A_7_hard);
DeclareAlarm(A_7_soft);

DeclareTask(T_8_L);
DeclareTask(T_8_H);
DeclareCounter(C_8_hard);
DeclareCounter(C_8_soft);
DeclareAlarm(A_8_hard);
DeclareAlarm(A_8_soft);

DeclareTask(T_9_L);
DeclareTask(T_9_H);
DeclareCounter(C_9_hard);
DeclareCounter(C_9_soft);
DeclareAlarm(A_9_hard);
DeclareAlarm(A_9_soft);

DeclareTask(T_10_L);
DeclareTask(T_10_H);
DeclareCounter(C_10_hard);
DeclareCounter(C_10_soft);
DeclareAlarm(A_10_hard);
DeclareAlarm(A_10_soft);

DeclareTask(T_11_L);
DeclareTask(T_11_H);
DeclareCounter(C_11_hard);
DeclareCounter(C_11_soft);
DeclareAlarm(A_11_hard);
DeclareAlarm(A_11_soft);

DeclareTask(T_12_L);
DeclareTask(T_12_H);
DeclareCounter(C_12_hard);
DeclareCounter(C_12_soft);
DeclareAlarm(A_12_hard);
DeclareAlarm(A_12_soft);

DeclareTask(T_13_L);
DeclareTask(T_13_H);
DeclareCounter(C_13_hard);
DeclareCounter(C_13_soft);
DeclareAlarm(A_13_hard);
DeclareAlarm(A_13_soft);

DeclareTask(T_14_L);
DeclareTask(T_14_H);
DeclareCounter(C_14_hard);
DeclareCounter(C_14_soft);
DeclareAlarm(A_14_hard);
DeclareAlarm(A_14_soft);

DeclareTask(T_15_L);
DeclareTask(T_15_H);
DeclareCounter(C_15_hard);
DeclareCounter(C_15_soft);
DeclareAlarm(A_15_hard);
DeclareAlarm(A_15_soft);

DeclareTask(T_16_L);
DeclareTask(T_16_H);
DeclareCounter(C_16_hard);
DeclareCounter(C_16_soft);
DeclareAlarm(A_16_hard);
DeclareAlarm(A_16_soft);

DeclareTask(T_17_L);
DeclareTask(T_17_H);
DeclareCounter(C_17_hard);
DeclareCounter(C_17_soft);
DeclareAlarm(A_17_hard);
DeclareAlarm(A_17_soft);

DeclareTask(T_18_L);
DeclareTask(T_18_H);
DeclareCounter(C_18_hard);
DeclareCounter(C_18_soft);
DeclareAlarm(A_18_hard);
DeclareAlarm(A_18_soft);

DeclareTask(T_19_L);
DeclareTask(T_19_H);
DeclareCounter(C_19_hard);
DeclareCounter(C_19_soft);
DeclareAlarm(A_19_hard);
DeclareAlarm(A_19_soft);

DeclareTask(T_20_L);
DeclareTask(T_20_H);
DeclareCounter(C_20_hard);
DeclareCounter(C_20_soft);
DeclareAlarm(A_20_hard);
DeclareAlarm(A_20_soft);

DeclareTask(T_21_L);
DeclareTask(T_21_H);
DeclareCounter(C_21_hard);
DeclareCounter(C_21_soft);
DeclareAlarm(A_21_hard);
DeclareAlarm(A_21_soft);

DeclareTask(T_22_L);
DeclareTask(T_22_H);
DeclareCounter(C_22_hard);
DeclareCounter(C_22_soft);
DeclareAlarm(A_22_hard);
DeclareAlarm(A_22_soft);

DeclareTask(T_23_L);
DeclareTask(T_23_H);
DeclareCounter(C_23_hard);
DeclareCounter(C_23_soft);
DeclareAlarm(A_23_hard);
DeclareAlarm(A_23_soft);

DeclareTask(T_24_L);
DeclareTask(T_24_H);
DeclareCounter(C_24_hard);
DeclareCounter(C_24_soft);
DeclareAlarm(A_24_hard);
DeclareAlarm(A_24_soft);

DeclareTask(T_25_L);
DeclareTask(T_25_H);
DeclareCounter(C_25_hard);
DeclareCounter(C_25_soft);
DeclareAlarm(A_25_hard);
DeclareAlarm(A_25_soft);

DeclareTask(T_26_L);
DeclareTask(T_26_H);
DeclareCounter(C_26_hard);
DeclareCounter(C_26_soft);
DeclareAlarm(A_26_hard);
DeclareAlarm(A_26_soft);

DeclareTask(T_27_L);
DeclareTask(T_27_H);
DeclareCounter(C_27_hard);
DeclareCounter(C_27_soft);
DeclareAlarm(A_27_hard);
DeclareAlarm(A_27_soft);

DeclareTask(T_28_L);
DeclareTask(T_28_H);
DeclareCounter(C_28_hard);
DeclareCounter(C_28_soft);
DeclareAlarm(A_28_hard);
DeclareAlarm(A_28_soft);

DeclareTask(T_29_L);
DeclareTask(T_29_H);
DeclareCounter(C_29_hard);
DeclareCounter(C_29_soft);
DeclareAlarm(A_29_hard);
DeclareAlarm(A_29_soft);

DeclareTask(T_30_L);
DeclareTask(T_30_H);
DeclareCounter(C_30_hard);
DeclareCounter(C_30_soft);
DeclareAlarm(A_30_hard);
DeclareAlarm(A_30_soft);

DeclareTask(T_31_L);
DeclareTask(T_31_H);
DeclareCounter(C_31_hard);
DeclareCounter(C_31_soft);
DeclareAlarm(A_31_hard);
DeclareAlarm(A_31_soft);

DeclareTask(T_32_L);
DeclareTask(T_32_H);
DeclareCounter(C_32_hard);
DeclareCounter(C_32_soft);
DeclareAlarm(A_32_hard);
DeclareAlarm(A_32_soft);

DeclareTask(T_33_L);
DeclareTask(T_33_H);
DeclareCounter(C_33_hard);
DeclareCounter(C_33_soft);
DeclareAlarm(A_33_hard);
DeclareAlarm(A_33_soft);

DeclareTask(T_34_L);
DeclareTask(T_34_H);
DeclareCounter(C_34_hard);
DeclareCounter(C_34_soft);
DeclareAlarm(A_34_hard);
DeclareAlarm(A_34_soft);

DeclareTask(T_35_L);
DeclareTask(T_35_H);
DeclareCounter(C_35_hard);
DeclareCounter(C_35_soft);
DeclareAlarm(A_35_hard);
DeclareAlarm(A_35_soft);

DeclareTask(T_36_L);
DeclareTask(T_36_H);
DeclareCounter(C_36_hard);
DeclareCounter(C_36_soft);
DeclareAlarm(A_36_hard);
DeclareAlarm(A_36_soft);

DeclareTask(T_37_L);
DeclareTask(T_37_H);
DeclareCounter(C_37_hard);
DeclareCounter(C_37_soft);
DeclareAlarm(A_37_hard);
DeclareAlarm(A_37_soft);

DeclareTask(T_38_L);
DeclareTask(T_38_H);
DeclareCounter(C_38_hard);
DeclareCounter(C_38_soft);
DeclareAlarm(A_38_hard);
DeclareAlarm(A_38_soft);

DeclareTask(T_39_L);
DeclareTask(T_39_H);
DeclareCounter(C_39_hard);
DeclareCounter(C_39_soft);
DeclareAlarm(A_39_hard);
DeclareAlarm(A_39_soft);

DeclareTask(T_40_L);
DeclareTask(T_40_H);
DeclareCounter(C_40_hard);
DeclareCounter(C_40_soft);
DeclareAlarm(A_40_hard);
DeclareAlarm(A_40_soft);

DeclareTask(T_41_L);
DeclareTask(T_41_H);
DeclareCounter(C_41_hard);
DeclareCounter(C_41_soft);
DeclareAlarm(A_41_hard);
DeclareAlarm(A_41_soft);

DeclareTask(T_42_L);
DeclareTask(T_42_H);
DeclareCounter(C_42_hard);
DeclareCounter(C_42_soft);
DeclareAlarm(A_42_hard);
DeclareAlarm(A_42_soft);

DeclareTask(T_43_L);
DeclareTask(T_43_H);
DeclareCounter(C_43_hard);
DeclareCounter(C_43_soft);
DeclareAlarm(A_43_hard);
DeclareAlarm(A_43_soft);

DeclareTask(T_44_L);
DeclareTask(T_44_H);
DeclareCounter(C_44_hard);
DeclareCounter(C_44_soft);
DeclareAlarm(A_44_hard);
DeclareAlarm(A_44_soft);

DeclareTask(T_45_L);
DeclareTask(T_45_H);
DeclareCounter(C_45_hard);
DeclareCounter(C_45_soft);
DeclareAlarm(A_45_hard);
DeclareAlarm(A_45_soft);

DeclareTask(T_46_L);
DeclareTask(T_46_H);
DeclareCounter(C_46_hard);
DeclareCounter(C_46_soft);
DeclareAlarm(A_46_hard);
DeclareAlarm(A_46_soft);

DeclareTask(T_47_L);
DeclareTask(T_47_H);
DeclareCounter(C_47_hard);
DeclareCounter(C_47_soft);
DeclareAlarm(A_47_hard);
DeclareAlarm(A_47_soft);

DeclareTask(T_48_L);
DeclareTask(T_48_H);
DeclareCounter(C_48_hard);
DeclareCounter(C_48_soft);
DeclareAlarm(A_48_hard);
DeclareAlarm(A_48_soft);

DeclareTask(T_49_L);
DeclareTask(T_49_H);
DeclareCounter(C_49_hard);
DeclareCounter(C_49_soft);
DeclareAlarm(A_49_hard);
DeclareAlarm(A_49_soft);

DeclareTask(T_50_L);
DeclareTask(T_50_H);
DeclareCounter(C_50_hard);
DeclareCounter(C_50_soft);
DeclareAlarm(A_50_hard);
DeclareAlarm(A_50_soft);

DeclareTask(T_51_L);
DeclareTask(T_51_H);
DeclareCounter(C_51_hard);
DeclareCounter(C_51_soft);
DeclareAlarm(A_51_hard);
DeclareAlarm(A_51_soft);

DeclareTask(T_52_L);
DeclareTask(T_52_H);
DeclareCounter(C_52_hard);
DeclareCounter(C_52_soft);
DeclareAlarm(A_52_hard);
DeclareAlarm(A_52_soft);

DeclareTask(T_53_L);
DeclareTask(T_53_H);
DeclareCounter(C_53_hard);
DeclareCounter(C_53_soft);
DeclareAlarm(A_53_hard);
DeclareAlarm(A_53_soft);

DeclareTask(T_54_L);
DeclareTask(T_54_H);
DeclareCounter(C_54_hard);
DeclareCounter(C_54_soft);
DeclareAlarm(A_54_hard);
DeclareAlarm(A_54_soft);

DeclareTask(T_55_L);
DeclareTask(T_55_H);
DeclareCounter(C_55_hard);
DeclareCounter(C_55_soft);
DeclareAlarm(A_55_hard);
DeclareAlarm(A_55_soft);

DeclareTask(T_56_L);
DeclareTask(T_56_H);
DeclareCounter(C_56_hard);
DeclareCounter(C_56_soft);
DeclareAlarm(A_56_hard);
DeclareAlarm(A_56_soft);

DeclareTask(T_57_L);
DeclareTask(T_57_H);
DeclareCounter(C_57_hard);
DeclareCounter(C_57_soft);
DeclareAlarm(A_57_hard);
DeclareAlarm(A_57_soft);

DeclareTask(T_58_L);
DeclareTask(T_58_H);
DeclareCounter(C_58_hard);
DeclareCounter(C_58_soft);
DeclareAlarm(A_58_hard);
DeclareAlarm(A_58_soft);

DeclareTask(T_59_L);
DeclareTask(T_59_H);
DeclareCounter(C_59_hard);
DeclareCounter(C_59_soft);
DeclareAlarm(A_59_hard);
DeclareAlarm(A_59_soft);

DeclareTask(T_60_L);
DeclareTask(T_60_H);
DeclareCounter(C_60_hard);
DeclareCounter(C_60_soft);
DeclareAlarm(A_60_hard);
DeclareAlarm(A_60_soft);

DeclareTask(T_61_L);
DeclareTask(T_61_H);
DeclareCounter(C_61_hard);
DeclareCounter(C_61_soft);
DeclareAlarm(A_61_hard);
DeclareAlarm(A_61_soft);

DeclareTask(T_62_L);
DeclareTask(T_62_H);
DeclareCounter(C_62_hard);
DeclareCounter(C_62_soft);
DeclareAlarm(A_62_hard);
DeclareAlarm(A_62_soft);

DeclareTask(T_63_L);
DeclareTask(T_63_H);
DeclareCounter(C_63_hard);
DeclareCounter(C_63_soft);
DeclareAlarm(A_63_hard);
DeclareAlarm(A_63_soft);

DeclareTask(T_64_L);
DeclareTask(T_64_H);
DeclareCounter(C_64_hard);
DeclareCounter(C_64_soft);
DeclareAlarm(A_64_hard);
DeclareAlarm(A_64_soft);

DeclareTask(T_65_L);
DeclareTask(T_65_H);
DeclareCounter(C_65_hard);
DeclareCounter(C_65_soft);
DeclareAlarm(A_65_hard);
DeclareAlarm(A_65_soft);

DeclareTask(T_66_L);
DeclareTask(T_66_H);
DeclareCounter(C_66_hard);
DeclareCounter(C_66_soft);
DeclareAlarm(A_66_hard);
DeclareAlarm(A_66_soft);

DeclareTask(T_67_L);
DeclareTask(T_67_H);
DeclareCounter(C_67_hard);
DeclareCounter(C_67_soft);
DeclareAlarm(A_67_hard);
DeclareAlarm(A_67_soft);

DeclareTask(T_68_L);
DeclareTask(T_68_H);
DeclareCounter(C_68_hard);
DeclareCounter(C_68_soft);
DeclareAlarm(A_68_hard);
DeclareAlarm(A_68_soft);

DeclareTask(T_69_L);
DeclareTask(T_69_H);
DeclareCounter(C_69_hard);
DeclareCounter(C_69_soft);
DeclareAlarm(A_69_hard);
DeclareAlarm(A_69_soft);

DeclareTask(T_70_L);
DeclareTask(T_70_H);
DeclareCounter(C_70_hard);
DeclareCounter(C_70_soft);
DeclareAlarm(A_70_hard);
DeclareAlarm(A_70_soft);

DeclareTask(T_71_L);
DeclareTask(T_71_H);
DeclareCounter(C_71_hard);
DeclareCounter(C_71_soft);
DeclareAlarm(A_71_hard);
DeclareAlarm(A_71_soft);

DeclareTask(T_72_L);
DeclareTask(T_72_H);
DeclareCounter(C_72_hard);
DeclareCounter(C_72_soft);
DeclareAlarm(A_72_hard);
DeclareAlarm(A_72_soft);

DeclareTask(T_73_L);
DeclareTask(T_73_H);
DeclareCounter(C_73_hard);
DeclareCounter(C_73_soft);
DeclareAlarm(A_73_hard);
DeclareAlarm(A_73_soft);

DeclareTask(T_74_L);
DeclareTask(T_74_H);
DeclareCounter(C_74_hard);
DeclareCounter(C_74_soft);
DeclareAlarm(A_74_hard);
DeclareAlarm(A_74_soft);

DeclareTask(T_75_L);
DeclareTask(T_75_H);
DeclareCounter(C_75_hard);
DeclareCounter(C_75_soft);
DeclareAlarm(A_75_hard);
DeclareAlarm(A_75_soft);

DeclareTask(T_76_L);
DeclareTask(T_76_H);
DeclareCounter(C_76_hard);
DeclareCounter(C_76_soft);
DeclareAlarm(A_76_hard);
DeclareAlarm(A_76_soft);

DeclareTask(T_77_L);
DeclareTask(T_77_H);
DeclareCounter(C_77_hard);
DeclareCounter(C_77_soft);
DeclareAlarm(A_77_hard);
DeclareAlarm(A_77_soft);

DeclareTask(T_78_L);
DeclareTask(T_78_H);
DeclareCounter(C_78_hard);
DeclareCounter(C_78_soft);
DeclareAlarm(A_78_hard);
DeclareAlarm(A_78_soft);

DeclareTask(T_79_L);
DeclareTask(T_79_H);
DeclareCounter(C_79_hard);
DeclareCounter(C_79_soft);
DeclareAlarm(A_79_hard);
DeclareAlarm(A_79_soft);

DeclareTask(T_80_L);
DeclareTask(T_80_H);
DeclareCounter(C_80_hard);
DeclareCounter(C_80_soft);
DeclareAlarm(A_80_hard);
DeclareAlarm(A_80_soft);

DeclareTask(T_81_L);
DeclareTask(T_81_H);
DeclareCounter(C_81_hard);
DeclareCounter(C_81_soft);
DeclareAlarm(A_81_hard);
DeclareAlarm(A_81_soft);

DeclareTask(T_82_L);
DeclareTask(T_82_H);
DeclareCounter(C_82_hard);
DeclareCounter(C_82_soft);
DeclareAlarm(A_82_hard);
DeclareAlarm(A_82_soft);

DeclareTask(T_83_L);
DeclareTask(T_83_H);
DeclareCounter(C_83_hard);
DeclareCounter(C_83_soft);
DeclareAlarm(A_83_hard);
DeclareAlarm(A_83_soft);

DeclareTask(T_84_L);
DeclareTask(T_84_H);
DeclareCounter(C_84_hard);
DeclareCounter(C_84_soft);
DeclareAlarm(A_84_hard);
DeclareAlarm(A_84_soft);

DeclareTask(T_85_L);
DeclareTask(T_85_H);
DeclareCounter(C_85_hard);
DeclareCounter(C_85_soft);
DeclareAlarm(A_85_hard);
DeclareAlarm(A_85_soft);

DeclareTask(T_86_L);
DeclareTask(T_86_H);
DeclareCounter(C_86_hard);
DeclareCounter(C_86_soft);
DeclareAlarm(A_86_hard);
DeclareAlarm(A_86_soft);

DeclareTask(T_87_L);
DeclareTask(T_87_H);
DeclareCounter(C_87_hard);
DeclareCounter(C_87_soft);
DeclareAlarm(A_87_hard);
DeclareAlarm(A_87_soft);

DeclareTask(T_88_L);
DeclareTask(T_88_H);
DeclareCounter(C_88_hard);
DeclareCounter(C_88_soft);
DeclareAlarm(A_88_hard);
DeclareAlarm(A_88_soft);

DeclareTask(T_89_L);
DeclareTask(T_89_H);
DeclareCounter(C_89_hard);
DeclareCounter(C_89_soft);
DeclareAlarm(A_89_hard);
DeclareAlarm(A_89_soft);

DeclareTask(T_90_L);
DeclareTask(T_90_H);
DeclareCounter(C_90_hard);
DeclareCounter(C_90_soft);
DeclareAlarm(A_90_hard);
DeclareAlarm(A_90_soft);

DeclareTask(T_91_L);
DeclareTask(T_91_H);
DeclareCounter(C_91_hard);
DeclareCounter(C_91_soft);
DeclareAlarm(A_91_hard);
DeclareAlarm(A_91_soft);

DeclareTask(T_92_L);
DeclareTask(T_92_H);
DeclareCounter(C_92_hard);
DeclareCounter(C_92_soft);
DeclareAlarm(A_92_hard);
DeclareAlarm(A_92_soft);

DeclareTask(T_93_L);
DeclareTask(T_93_H);
DeclareCounter(C_93_hard);
DeclareCounter(C_93_soft);
DeclareAlarm(A_93_hard);
DeclareAlarm(A_93_soft);

DeclareTask(T_94_L);
DeclareTask(T_94_H);
DeclareCounter(C_94_hard);
DeclareCounter(C_94_soft);
DeclareAlarm(A_94_hard);
DeclareAlarm(A_94_soft);

DeclareTask(T_95_L);
DeclareTask(T_95_H);
DeclareCounter(C_95_hard);
DeclareCounter(C_95_soft);
DeclareAlarm(A_95_hard);
DeclareAlarm(A_95_soft);

DeclareTask(T_96_L);
DeclareTask(T_96_H);
DeclareCounter(C_96_hard);
DeclareCounter(C_96_soft);
DeclareAlarm(A_96_hard);
DeclareAlarm(A_96_soft);

DeclareTask(T_97_L);
DeclareTask(T_97_H);
DeclareCounter(C_97_hard);
DeclareCounter(C_97_soft);
DeclareAlarm(A_97_hard);
DeclareAlarm(A_97_soft);

DeclareTask(T_98_L);
DeclareTask(T_98_H);
DeclareCounter(C_98_hard);
DeclareCounter(C_98_soft);
DeclareAlarm(A_98_hard);
DeclareAlarm(A_98_soft);

DeclareTask(T_99_L);
DeclareTask(T_99_H);
DeclareCounter(C_99_hard);
DeclareCounter(C_99_soft);
DeclareAlarm(A_99_hard);
DeclareAlarm(A_99_soft);

DeclareTask(T_100_L);
DeclareTask(T_100_H);
DeclareCounter(C_100_hard);
DeclareCounter(C_100_soft);
DeclareAlarm(A_100_hard);
DeclareAlarm(A_100_soft);

DeclareTask(T_101_L);
DeclareTask(T_101_H);
DeclareCounter(C_101_hard);
DeclareCounter(C_101_soft);
DeclareAlarm(A_101_hard);
DeclareAlarm(A_101_soft);

DeclareTask(T_102_L);
DeclareTask(T_102_H);
DeclareCounter(C_102_hard);
DeclareCounter(C_102_soft);
DeclareAlarm(A_102_hard);
DeclareAlarm(A_102_soft);

DeclareTask(T_103_L);
DeclareTask(T_103_H);
DeclareCounter(C_103_hard);
DeclareCounter(C_103_soft);
DeclareAlarm(A_103_hard);
DeclareAlarm(A_103_soft);

DeclareTask(T_104_L);
DeclareTask(T_104_H);
DeclareCounter(C_104_hard);
DeclareCounter(C_104_soft);
DeclareAlarm(A_104_hard);
DeclareAlarm(A_104_soft);

DeclareTask(T_105_L);
DeclareTask(T_105_H);
DeclareCounter(C_105_hard);
DeclareCounter(C_105_soft);
DeclareAlarm(A_105_hard);
DeclareAlarm(A_105_soft);

DeclareTask(T_106_L);
DeclareTask(T_106_H);
DeclareCounter(C_106_hard);
DeclareCounter(C_106_soft);
DeclareAlarm(A_106_hard);
DeclareAlarm(A_106_soft);

DeclareTask(T_107_L);
DeclareTask(T_107_H);
DeclareCounter(C_107_hard);
DeclareCounter(C_107_soft);
DeclareAlarm(A_107_hard);
DeclareAlarm(A_107_soft);

DeclareTask(T_108_L);
DeclareTask(T_108_H);
DeclareCounter(C_108_hard);
DeclareCounter(C_108_soft);
DeclareAlarm(A_108_hard);
DeclareAlarm(A_108_soft);

DeclareTask(T_109_L);
DeclareTask(T_109_H);
DeclareCounter(C_109_hard);
DeclareCounter(C_109_soft);
DeclareAlarm(A_109_hard);
DeclareAlarm(A_109_soft);

DeclareTask(T_110_L);
DeclareTask(T_110_H);
DeclareCounter(C_110_hard);
DeclareCounter(C_110_soft);
DeclareAlarm(A_110_hard);
DeclareAlarm(A_110_soft);

DeclareTask(T_111_L);
DeclareTask(T_111_H);
DeclareCounter(C_111_hard);
DeclareCounter(C_111_soft);
DeclareAlarm(A_111_hard);
DeclareAlarm(A_111_soft);

DeclareTask(T_112_L);
DeclareTask(T_112_H);
DeclareCounter(C_112_hard);
DeclareCounter(C_112_soft);
DeclareAlarm(A_112_hard);
DeclareAlarm(A_112_soft);

DeclareTask(T_113_L);
DeclareTask(T_113_H);
DeclareCounter(C_113_hard);
DeclareCounter(C_113_soft);
DeclareAlarm(A_113_hard);
DeclareAlarm(A_113_soft);

DeclareTask(T_114_L);
DeclareTask(T_114_H);
DeclareCounter(C_114_hard);
DeclareCounter(C_114_soft);
DeclareAlarm(A_114_hard);
DeclareAlarm(A_114_soft);

DeclareTask(T_115_L);
DeclareTask(T_115_H);
DeclareCounter(C_115_hard);
DeclareCounter(C_115_soft);
DeclareAlarm(A_115_hard);
DeclareAlarm(A_115_soft);

DeclareTask(T_116_L);
DeclareTask(T_116_H);
DeclareCounter(C_116_hard);
DeclareCounter(C_116_soft);
DeclareAlarm(A_116_hard);
DeclareAlarm(A_116_soft);

DeclareTask(T_117_L);
DeclareTask(T_117_H);
DeclareCounter(C_117_hard);
DeclareCounter(C_117_soft);
DeclareAlarm(A_117_hard);
DeclareAlarm(A_117_soft);

DeclareTask(T_118_L);
DeclareTask(T_118_H);
DeclareCounter(C_118_hard);
DeclareCounter(C_118_soft);
DeclareAlarm(A_118_hard);
DeclareAlarm(A_118_soft);

DeclareTask(T_119_L);
DeclareTask(T_119_H);
DeclareCounter(C_119_hard);
DeclareCounter(C_119_soft);
DeclareAlarm(A_119_hard);
DeclareAlarm(A_119_soft);

DeclareTask(T_120_L);
DeclareTask(T_120_H);
DeclareCounter(C_120_hard);
DeclareCounter(C_120_soft);
DeclareAlarm(A_120_hard);
DeclareAlarm(A_120_soft);

DeclareTask(T_121_L);
DeclareTask(T_121_H);
DeclareCounter(C_121_hard);
DeclareCounter(C_121_soft);
DeclareAlarm(A_121_hard);
DeclareAlarm(A_121_soft);

DeclareTask(T_122_L);
DeclareTask(T_122_H);
DeclareCounter(C_122_hard);
DeclareCounter(C_122_soft);
DeclareAlarm(A_122_hard);
DeclareAlarm(A_122_soft);

DeclareTask(T_123_L);
DeclareTask(T_123_H);
DeclareCounter(C_123_hard);
DeclareCounter(C_123_soft);
DeclareAlarm(A_123_hard);
DeclareAlarm(A_123_soft);

DeclareTask(T_124_L);
DeclareTask(T_124_H);
DeclareCounter(C_124_hard);
DeclareCounter(C_124_soft);
DeclareAlarm(A_124_hard);
DeclareAlarm(A_124_soft);

DeclareTask(T_125_L);
DeclareTask(T_125_H);
DeclareCounter(C_125_hard);
DeclareCounter(C_125_soft);
DeclareAlarm(A_125_hard);
DeclareAlarm(A_125_soft);


TASK(T_1_L) {
        int idx = (1 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_1_soft);
        // kout << "LowTask 1" << endl;
        GetAlarm(A_1_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_1_H) {
        uint32_t idx = (1 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_1_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_58_to_1 != 0xaa) { data = Calc(idx, ticks); }; comm_58_to_1 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_2_L) {
        int idx = (2 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_2_soft);
        // kout << "LowTask 2" << endl;
        GetAlarm(A_2_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_2_H) {
        uint32_t idx = (2 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_2_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_106_H);
}
        

TASK(T_3_L) {
        int idx = (3 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_3_soft);
        // kout << "LowTask 3" << endl;
        GetAlarm(A_3_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_3_H) {
        uint32_t idx = (3 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_3_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_53_to_3 != 0xaa) { data = Calc(idx, ticks); }; comm_53_to_3 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_4_L) {
        int idx = (4 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_4_soft);
        // kout << "LowTask 4" << endl;
        GetAlarm(A_4_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_4_H) {
        uint32_t idx = (4 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_4_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_5_L) {
        int idx = (5 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_5_soft);
        // kout << "LowTask 5" << endl;
        GetAlarm(A_5_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_5_H) {
        uint32_t idx = (5 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_5_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_6_L) {
        int idx = (6 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_6_soft);
        // kout << "LowTask 6" << endl;
        GetAlarm(A_6_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_6_H) {
        uint32_t idx = (6 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_6_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_7_L) {
        int idx = (7 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_7_soft);
        // kout << "LowTask 7" << endl;
        GetAlarm(A_7_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_7_H) {
        uint32_t idx = (7 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_7_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_8_L) {
        int idx = (8 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_8_soft);
        // kout << "LowTask 8" << endl;
        GetAlarm(A_8_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_8_H) {
        uint32_t idx = (8 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_8_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_9_L) {
        int idx = (9 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_9_soft);
        // kout << "LowTask 9" << endl;
        GetAlarm(A_9_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_9_H) {
        uint32_t idx = (9 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_9_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_10_L) {
        int idx = (10 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_10_soft);
        // kout << "LowTask 10" << endl;
        GetAlarm(A_10_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_5_L);
        TerminateTask();
}
        

TASK(T_10_H) {
        uint32_t idx = (10 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_10_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_11_L) {
        int idx = (11 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_11_soft);
        // kout << "LowTask 11" << endl;
        GetAlarm(A_11_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_90_H);
}
        

TASK(T_11_H) {
        uint32_t idx = (11 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_11_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_12_L) {
        int idx = (12 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_12_soft);
        // kout << "LowTask 12" << endl;
        GetAlarm(A_12_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_12_H) {
        uint32_t idx = (12 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_12_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_13_L) {
        int idx = (13 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_13_soft);
        // kout << "LowTask 13" << endl;
        GetAlarm(A_13_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_13_H) {
        uint32_t idx = (13 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_13_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_30_H);
}
        

TASK(T_14_L) {
        int idx = (14 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_14_soft);
        // kout << "LowTask 14" << endl;
        GetAlarm(A_14_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_14_H) {
        uint32_t idx = (14 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_14_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_15_L) {
        int idx = (15 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_15_soft);
        // kout << "LowTask 15" << endl;
        GetAlarm(A_15_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_15_H) {
        uint32_t idx = (15 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_15_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_112_to_15 != 0xaa) { data = Calc(idx, ticks); }; comm_112_to_15 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_16_L) {
        int idx = (16 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_16_soft);
        // kout << "LowTask 16" << endl;
        GetAlarm(A_16_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_16_H) {
        uint32_t idx = (16 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_16_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_17_L) {
        int idx = (17 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_17_soft);
        // kout << "LowTask 17" << endl;
        GetAlarm(A_17_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_17_H) {
        uint32_t idx = (17 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_17_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_18_L) {
        int idx = (18 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_18_soft);
        // kout << "LowTask 18" << endl;
        GetAlarm(A_18_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_54_H);
}
        

TASK(T_18_H) {
        uint32_t idx = (18 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_18_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_19_L) {
        int idx = (19 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_19_soft);
        // kout << "LowTask 19" << endl;
        GetAlarm(A_19_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_19_H) {
        uint32_t idx = (19 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_19_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_20_L) {
        int idx = (20 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_20_soft);
        // kout << "LowTask 20" << endl;
        GetAlarm(A_20_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_20_H) {
        uint32_t idx = (20 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_20_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_71_H);
}
        

TASK(T_21_L) {
        int idx = (21 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_21_soft);
        // kout << "LowTask 21" << endl;
        GetAlarm(A_21_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_21_H) {
        uint32_t idx = (21 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_21_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_22_L) {
        int idx = (22 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_22_soft);
        // kout << "LowTask 22" << endl;
        GetAlarm(A_22_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_22_H) {
        uint32_t idx = (22 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_22_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_23_L) {
        int idx = (23 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_23_soft);
        // kout << "LowTask 23" << endl;
        GetAlarm(A_23_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_28_H);
}
        

TASK(T_23_H) {
        uint32_t idx = (23 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_23_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_24_L) {
        int idx = (24 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_24_soft);
        // kout << "LowTask 24" << endl;
        GetAlarm(A_24_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_24_H) {
        uint32_t idx = (24 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_24_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_125_H);
}
        

TASK(T_25_L) {
        int idx = (25 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_25_soft);
        // kout << "LowTask 25" << endl;
        GetAlarm(A_25_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_25_H) {
        uint32_t idx = (25 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_25_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_26_L) {
        int idx = (26 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_26_soft);
        // kout << "LowTask 26" << endl;
        GetAlarm(A_26_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_48_H);
}
        

TASK(T_26_H) {
        uint32_t idx = (26 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_26_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_27_L) {
        int idx = (27 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_27_soft);
        // kout << "LowTask 27" << endl;
        GetAlarm(A_27_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_27_H) {
        uint32_t idx = (27 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_27_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_100_to_27 != 0xaa) { data = Calc(idx, ticks); }; comm_100_to_27 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_28_L) {
        int idx = (28 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_28_soft);
        // kout << "LowTask 28" << endl;
        GetAlarm(A_28_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_28_H) {
        uint32_t idx = (28 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_28_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_29_L) {
        int idx = (29 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_29_soft);
        // kout << "LowTask 29" << endl;
        GetAlarm(A_29_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_29_H) {
        uint32_t idx = (29 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_29_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_91_to_29 != 0xaa) { data = Calc(idx, ticks); }; comm_91_to_29 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_30_L) {
        int idx = (30 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_30_soft);
        // kout << "LowTask 30" << endl;
        GetAlarm(A_30_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_30_H) {
        uint32_t idx = (30 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_30_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_31_L) {
        int idx = (31 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_31_soft);
        // kout << "LowTask 31" << endl;
        GetAlarm(A_31_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_31_H) {
        uint32_t idx = (31 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_31_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_80_to_31 != 0xaa) { data = Calc(idx, ticks); }; comm_80_to_31 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_32_L) {
        int idx = (32 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_32_soft);
        // kout << "LowTask 32" << endl;
        GetAlarm(A_32_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_32_H) {
        uint32_t idx = (32 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_32_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_33_L) {
        int idx = (33 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_33_soft);
        // kout << "LowTask 33" << endl;
        GetAlarm(A_33_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_124_H);
}
        

TASK(T_33_H) {
        uint32_t idx = (33 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_33_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_34_L) {
        int idx = (34 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_34_soft);
        // kout << "LowTask 34" << endl;
        GetAlarm(A_34_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_34_H) {
        uint32_t idx = (34 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_34_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_35_L) {
        int idx = (35 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_35_soft);
        // kout << "LowTask 35" << endl;
        GetAlarm(A_35_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_35_H) {
        uint32_t idx = (35 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_35_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_64_to_35 != 0xaa) { data = Calc(idx, ticks); }; comm_64_to_35 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_36_L) {
        int idx = (36 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_36_soft);
        // kout << "LowTask 36" << endl;
        GetAlarm(A_36_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_36_H) {
        uint32_t idx = (36 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_36_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_89_H);
}
        

TASK(T_37_L) {
        int idx = (37 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_37_soft);
        // kout << "LowTask 37" << endl;
        GetAlarm(A_37_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_37_H) {
        uint32_t idx = (37 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_37_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_38_L) {
        int idx = (38 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_38_soft);
        // kout << "LowTask 38" << endl;
        GetAlarm(A_38_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_38_H) {
        uint32_t idx = (38 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_38_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_39_L) {
        int idx = (39 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_39_soft);
        // kout << "LowTask 39" << endl;
        GetAlarm(A_39_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_39_H) {
        uint32_t idx = (39 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_39_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_40_L) {
        int idx = (40 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_40_soft);
        // kout << "LowTask 40" << endl;
        GetAlarm(A_40_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_40_H) {
        uint32_t idx = (40 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_40_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_41_L) {
        int idx = (41 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_41_soft);
        // kout << "LowTask 41" << endl;
        GetAlarm(A_41_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_41_H) {
        uint32_t idx = (41 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_41_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_42_L) {
        int idx = (42 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_42_soft);
        // kout << "LowTask 42" << endl;
        GetAlarm(A_42_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_42_H) {
        uint32_t idx = (42 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_42_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_114_H);
}
        

TASK(T_43_L) {
        int idx = (43 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_43_soft);
        // kout << "LowTask 43" << endl;
        GetAlarm(A_43_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_43_H) {
        uint32_t idx = (43 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_43_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_44_L) {
        int idx = (44 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_44_soft);
        // kout << "LowTask 44" << endl;
        GetAlarm(A_44_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_44_H) {
        uint32_t idx = (44 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_44_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_45_L) {
        int idx = (45 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_45_soft);
        // kout << "LowTask 45" << endl;
        GetAlarm(A_45_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_45_H) {
        uint32_t idx = (45 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_45_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_46_L) {
        int idx = (46 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_46_soft);
        // kout << "LowTask 46" << endl;
        GetAlarm(A_46_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_46_H) {
        uint32_t idx = (46 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_46_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_47_L) {
        int idx = (47 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_47_soft);
        // kout << "LowTask 47" << endl;
        GetAlarm(A_47_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_98_H);
}
        

TASK(T_47_H) {
        uint32_t idx = (47 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_47_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_48_L) {
        int idx = (48 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_48_soft);
        // kout << "LowTask 48" << endl;
        GetAlarm(A_48_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_48_H) {
        uint32_t idx = (48 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_48_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_49_L) {
        int idx = (49 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_49_soft);
        // kout << "LowTask 49" << endl;
        GetAlarm(A_49_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_49_H) {
        uint32_t idx = (49 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_49_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_50_L) {
        int idx = (50 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_50_soft);
        // kout << "LowTask 50" << endl;
        GetAlarm(A_50_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_50_H) {
        uint32_t idx = (50 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_50_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_51_L) {
        int idx = (51 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_51_soft);
        // kout << "LowTask 51" << endl;
        GetAlarm(A_51_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_51_H) {
        uint32_t idx = (51 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_51_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_52_L) {
        int idx = (52 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_52_soft);
        // kout << "LowTask 52" << endl;
        GetAlarm(A_52_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_52_H) {
        uint32_t idx = (52 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_52_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_53_L) {
        int idx = (53 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_53_soft);
        // kout << "LowTask 53" << endl;
        GetAlarm(A_53_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_53_H) {
        uint32_t idx = (53 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_53_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_53_to_3 = 0xaa;
        TerminateTask();
}
        

TASK(T_54_L) {
        int idx = (54 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_54_soft);
        // kout << "LowTask 54" << endl;
        GetAlarm(A_54_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_54_H) {
        uint32_t idx = (54 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_54_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_55_L) {
        int idx = (55 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_55_soft);
        // kout << "LowTask 55" << endl;
        GetAlarm(A_55_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_17_L);
        TerminateTask();
}
        

TASK(T_55_H) {
        uint32_t idx = (55 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_55_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_56_L) {
        int idx = (56 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_56_soft);
        // kout << "LowTask 56" << endl;
        GetAlarm(A_56_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_4_L);
        TerminateTask();
}
        

TASK(T_56_H) {
        uint32_t idx = (56 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_56_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_57_L) {
        int idx = (57 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_57_soft);
        // kout << "LowTask 57" << endl;
        GetAlarm(A_57_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_57_H) {
        uint32_t idx = (57 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_57_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_121_H);
}
        

TASK(T_58_L) {
        int idx = (58 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_58_soft);
        // kout << "LowTask 58" << endl;
        GetAlarm(A_58_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_58_H) {
        uint32_t idx = (58 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_58_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_58_to_1 = 0xaa;
        TerminateTask();
}
        

TASK(T_59_L) {
        int idx = (59 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_59_soft);
        // kout << "LowTask 59" << endl;
        GetAlarm(A_59_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_59_H) {
        uint32_t idx = (59 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_59_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_97_H);
}
        

TASK(T_60_L) {
        int idx = (60 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_60_soft);
        // kout << "LowTask 60" << endl;
        GetAlarm(A_60_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_60_H) {
        uint32_t idx = (60 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_60_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_68_to_60 != 0xaa) { data = Calc(idx, ticks); }; comm_68_to_60 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_61_L) {
        int idx = (61 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_61_soft);
        // kout << "LowTask 61" << endl;
        GetAlarm(A_61_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_122_H);
}
        

TASK(T_61_H) {
        uint32_t idx = (61 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_61_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_62_L) {
        int idx = (62 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_62_soft);
        // kout << "LowTask 62" << endl;
        GetAlarm(A_62_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_62_H) {
        uint32_t idx = (62 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_62_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_63_L) {
        int idx = (63 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_63_soft);
        // kout << "LowTask 63" << endl;
        GetAlarm(A_63_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_63_H) {
        uint32_t idx = (63 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_63_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        ChainTask(T_102_H);
}
        

TASK(T_64_L) {
        int idx = (64 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_64_soft);
        // kout << "LowTask 64" << endl;
        GetAlarm(A_64_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_64_H) {
        uint32_t idx = (64 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_64_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_64_to_35 = 0xaa;
        TerminateTask();
}
        

TASK(T_65_L) {
        int idx = (65 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_65_soft);
        // kout << "LowTask 65" << endl;
        GetAlarm(A_65_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_21_L);
        TerminateTask();
}
        

TASK(T_65_H) {
        uint32_t idx = (65 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_65_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_66_L) {
        int idx = (66 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_66_soft);
        // kout << "LowTask 66" << endl;
        GetAlarm(A_66_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_52_L);
        TerminateTask();
}
        

TASK(T_66_H) {
        uint32_t idx = (66 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_66_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_67_L) {
        int idx = (67 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_67_soft);
        // kout << "LowTask 67" << endl;
        GetAlarm(A_67_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_32_L);
        TerminateTask();
}
        

TASK(T_67_H) {
        uint32_t idx = (67 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_67_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_68_L) {
        int idx = (68 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_68_soft);
        // kout << "LowTask 68" << endl;
        GetAlarm(A_68_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_68_H) {
        uint32_t idx = (68 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_68_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_68_to_60 = 0xaa;
        TerminateTask();
}
        

TASK(T_69_L) {
        int idx = (69 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_69_soft);
        // kout << "LowTask 69" << endl;
        GetAlarm(A_69_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_69_H) {
        uint32_t idx = (69 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_69_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_70_L) {
        int idx = (70 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_70_soft);
        // kout << "LowTask 70" << endl;
        GetAlarm(A_70_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_70_H) {
        uint32_t idx = (70 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_70_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_71_L) {
        int idx = (71 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_71_soft);
        // kout << "LowTask 71" << endl;
        GetAlarm(A_71_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_71_H) {
        uint32_t idx = (71 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_71_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_72_L) {
        int idx = (72 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_72_soft);
        // kout << "LowTask 72" << endl;
        GetAlarm(A_72_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_72_H) {
        uint32_t idx = (72 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_72_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_79_to_72 != 0xaa) { data = Calc(idx, ticks); }; comm_79_to_72 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_73_L) {
        int idx = (73 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_73_soft);
        // kout << "LowTask 73" << endl;
        GetAlarm(A_73_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_73_H) {
        uint32_t idx = (73 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_73_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_74_L) {
        int idx = (74 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_74_soft);
        // kout << "LowTask 74" << endl;
        GetAlarm(A_74_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_74_H) {
        uint32_t idx = (74 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_74_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_75_L) {
        int idx = (75 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_75_soft);
        // kout << "LowTask 75" << endl;
        GetAlarm(A_75_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_75_H) {
        uint32_t idx = (75 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_75_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_76_L) {
        int idx = (76 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_76_soft);
        // kout << "LowTask 76" << endl;
        GetAlarm(A_76_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_25_L);
        TerminateTask();
}
        

TASK(T_76_H) {
        uint32_t idx = (76 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_76_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_77_L) {
        int idx = (77 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_77_soft);
        // kout << "LowTask 77" << endl;
        GetAlarm(A_77_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_77_H) {
        uint32_t idx = (77 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_77_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_78_L) {
        int idx = (78 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_78_soft);
        // kout << "LowTask 78" << endl;
        GetAlarm(A_78_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_119_H);
}
        

TASK(T_78_H) {
        uint32_t idx = (78 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_78_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_79_L) {
        int idx = (79 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_79_soft);
        // kout << "LowTask 79" << endl;
        GetAlarm(A_79_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_79_H) {
        uint32_t idx = (79 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_79_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_79_to_72 = 0xaa;
        TerminateTask();
}
        

TASK(T_80_L) {
        int idx = (80 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_80_soft);
        // kout << "LowTask 80" << endl;
        GetAlarm(A_80_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_80_H) {
        uint32_t idx = (80 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_80_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_80_to_31 = 0xaa;
        TerminateTask();
}
        

TASK(T_81_L) {
        int idx = (81 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_81_soft);
        // kout << "LowTask 81" << endl;
        GetAlarm(A_81_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_81_H) {
        uint32_t idx = (81 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_81_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_82_L) {
        int idx = (82 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_82_soft);
        // kout << "LowTask 82" << endl;
        GetAlarm(A_82_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_82_H) {
        uint32_t idx = (82 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_82_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_83_L) {
        int idx = (83 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_83_soft);
        // kout << "LowTask 83" << endl;
        GetAlarm(A_83_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_83_H) {
        uint32_t idx = (83 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_83_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_84_to_83 != 0xaa) { data = Calc(idx, ticks); }; comm_84_to_83 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_84_L) {
        int idx = (84 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_84_soft);
        // kout << "LowTask 84" << endl;
        GetAlarm(A_84_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_84_H) {
        uint32_t idx = (84 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_84_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_84_to_83 = 0xaa;
        TerminateTask();
}
        

TASK(T_85_L) {
        int idx = (85 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_85_soft);
        // kout << "LowTask 85" << endl;
        GetAlarm(A_85_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_120_H);
}
        

TASK(T_85_H) {
        uint32_t idx = (85 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_85_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_86_L) {
        int idx = (86 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_86_soft);
        // kout << "LowTask 86" << endl;
        GetAlarm(A_86_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_86_H) {
        uint32_t idx = (86 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_86_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_87_L) {
        int idx = (87 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_87_soft);
        // kout << "LowTask 87" << endl;
        GetAlarm(A_87_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_87_H) {
        uint32_t idx = (87 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_87_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_88_L) {
        int idx = (88 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_88_soft);
        // kout << "LowTask 88" << endl;
        GetAlarm(A_88_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_88_H) {
        uint32_t idx = (88 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_88_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_89_L) {
        int idx = (89 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_89_soft);
        // kout << "LowTask 89" << endl;
        GetAlarm(A_89_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_89_H) {
        uint32_t idx = (89 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_89_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_90_L) {
        int idx = (90 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_90_soft);
        // kout << "LowTask 90" << endl;
        GetAlarm(A_90_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_90_H) {
        uint32_t idx = (90 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_90_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_91_L) {
        int idx = (91 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_91_soft);
        // kout << "LowTask 91" << endl;
        GetAlarm(A_91_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_91_H) {
        uint32_t idx = (91 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_91_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_91_to_29 = 0xaa;
        TerminateTask();
}
        

TASK(T_92_L) {
        int idx = (92 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_92_soft);
        // kout << "LowTask 92" << endl;
        GetAlarm(A_92_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_41_L);
        TerminateTask();
}
        

TASK(T_92_H) {
        uint32_t idx = (92 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_92_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_93_L) {
        int idx = (93 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_93_soft);
        // kout << "LowTask 93" << endl;
        GetAlarm(A_93_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_93_H) {
        uint32_t idx = (93 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_93_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_94_L) {
        int idx = (94 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_94_soft);
        // kout << "LowTask 94" << endl;
        GetAlarm(A_94_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        ChainTask(T_113_H);
}
        

TASK(T_94_H) {
        uint32_t idx = (94 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_94_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_95_L) {
        int idx = (95 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_95_soft);
        // kout << "LowTask 95" << endl;
        GetAlarm(A_95_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_95_H) {
        uint32_t idx = (95 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_95_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_96_to_95 != 0xaa) { data = Calc(idx, ticks); }; comm_96_to_95 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_96_L) {
        int idx = (96 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_96_soft);
        // kout << "LowTask 96" << endl;
        GetAlarm(A_96_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_96_H) {
        uint32_t idx = (96 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_96_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_96_to_95 = 0xaa;
        TerminateTask();
}
        

TASK(T_97_L) {
        int idx = (97 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_97_soft);
        // kout << "LowTask 97" << endl;
        GetAlarm(A_97_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_97_H) {
        uint32_t idx = (97 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_97_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_98_L) {
        int idx = (98 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_98_soft);
        // kout << "LowTask 98" << endl;
        GetAlarm(A_98_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_98_H) {
        uint32_t idx = (98 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_98_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_99_L) {
        int idx = (99 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_99_soft);
        // kout << "LowTask 99" << endl;
        GetAlarm(A_99_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_99_H) {
        uint32_t idx = (99 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_99_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_100_L) {
        int idx = (100 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_100_soft);
        // kout << "LowTask 100" << endl;
        GetAlarm(A_100_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_100_H) {
        uint32_t idx = (100 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_100_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_100_to_27 = 0xaa;
        TerminateTask();
}
        

TASK(T_101_L) {
        int idx = (101 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_101_soft);
        // kout << "LowTask 101" << endl;
        GetAlarm(A_101_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_101_H) {
        uint32_t idx = (101 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_101_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_102_L) {
        int idx = (102 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_102_soft);
        // kout << "LowTask 102" << endl;
        GetAlarm(A_102_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_102_H) {
        uint32_t idx = (102 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_102_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_103_L) {
        int idx = (103 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_103_soft);
        // kout << "LowTask 103" << endl;
        GetAlarm(A_103_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_87_L);
        TerminateTask();
}
        

TASK(T_103_H) {
        uint32_t idx = (103 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_103_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_104_L) {
        int idx = (104 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_104_soft);
        // kout << "LowTask 104" << endl;
        GetAlarm(A_104_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_104_H) {
        uint32_t idx = (104 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_104_soft, &ticks);

        data = Calc(idx, ticks);
	while(comm_108_to_104 != 0xaa) { data = Calc(idx, ticks); }; comm_108_to_104 = 00;

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_105_L) {
        int idx = (105 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_105_soft);
        // kout << "LowTask 105" << endl;
        GetAlarm(A_105_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_105_H) {
        uint32_t idx = (105 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_105_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_106_L) {
        int idx = (106 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_106_soft);
        // kout << "LowTask 106" << endl;
        GetAlarm(A_106_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_106_H) {
        uint32_t idx = (106 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_106_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_107_L) {
        int idx = (107 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_107_soft);
        // kout << "LowTask 107" << endl;
        GetAlarm(A_107_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_107_H) {
        uint32_t idx = (107 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_107_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_108_L) {
        int idx = (108 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_108_soft);
        // kout << "LowTask 108" << endl;
        GetAlarm(A_108_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_108_H) {
        uint32_t idx = (108 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_108_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_108_to_104 = 0xaa;
        TerminateTask();
}
        

TASK(T_109_L) {
        int idx = (109 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_109_soft);
        // kout << "LowTask 109" << endl;
        GetAlarm(A_109_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_109_H) {
        uint32_t idx = (109 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_109_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_110_L) {
        int idx = (110 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_110_soft);
        // kout << "LowTask 110" << endl;
        GetAlarm(A_110_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_110_H) {
        uint32_t idx = (110 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_110_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_111_L) {
        int idx = (111 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_111_soft);
        // kout << "LowTask 111" << endl;
        GetAlarm(A_111_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_111_H) {
        uint32_t idx = (111 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_111_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_112_L) {
        int idx = (112 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_112_soft);
        // kout << "LowTask 112" << endl;
        GetAlarm(A_112_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_112_H) {
        uint32_t idx = (112 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_112_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
	comm_112_to_15 = 0xaa;
        TerminateTask();
}
        

TASK(T_113_L) {
        int idx = (113 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_113_soft);
        // kout << "LowTask 113" << endl;
        GetAlarm(A_113_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_113_H) {
        uint32_t idx = (113 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_113_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_114_L) {
        int idx = (114 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_114_soft);
        // kout << "LowTask 114" << endl;
        GetAlarm(A_114_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_114_H) {
        uint32_t idx = (114 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_114_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_115_L) {
        int idx = (115 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_115_soft);
        // kout << "LowTask 115" << endl;
        GetAlarm(A_115_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_115_H) {
        uint32_t idx = (115 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_115_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_116_L) {
        int idx = (116 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_116_soft);
        // kout << "LowTask 116" << endl;
        GetAlarm(A_116_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_116_H) {
        uint32_t idx = (116 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_116_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_117_L) {
        int idx = (117 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_117_soft);
        // kout << "LowTask 117" << endl;
        GetAlarm(A_117_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_117_H) {
        uint32_t idx = (117 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_117_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_118_L) {
        int idx = (118 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_118_soft);
        // kout << "LowTask 118" << endl;
        GetAlarm(A_118_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_40_L);
        TerminateTask();
}
        

TASK(T_118_H) {
        uint32_t idx = (118 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_118_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_119_L) {
        int idx = (119 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_119_soft);
        // kout << "LowTask 119" << endl;
        GetAlarm(A_119_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_119_H) {
        uint32_t idx = (119 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_119_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_120_L) {
        int idx = (120 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_120_soft);
        // kout << "LowTask 120" << endl;
        GetAlarm(A_120_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_120_H) {
        uint32_t idx = (120 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_120_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_121_L) {
        int idx = (121 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_121_soft);
        // kout << "LowTask 121" << endl;
        GetAlarm(A_121_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_121_H) {
        uint32_t idx = (121 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_121_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_122_L) {
        int idx = (122 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_122_soft);
        // kout << "LowTask 122" << endl;
        GetAlarm(A_122_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_122_H) {
        uint32_t idx = (122 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_122_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_123_L) {
        int idx = (123 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_123_soft);
        // kout << "LowTask 123" << endl;
        GetAlarm(A_123_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
    ActivateTask(T_43_L);
        TerminateTask();
}
        

TASK(T_123_H) {
        uint32_t idx = (123 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_123_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_124_L) {
        int idx = (124 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_124_soft);
        // kout << "LowTask 124" << endl;
        GetAlarm(A_124_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_124_H) {
        uint32_t idx = (124 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_124_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        

TASK(T_125_L) {
        int idx = (125 - 1) << 1 | 0;
        TickType data;
        IncrementCounter(C_125_soft);
        // kout << "LowTask 125" << endl;
        GetAlarm(A_125_hard, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        /* Post Hook */
        TerminateTask();
}
        

TASK(T_125_H) {
        uint32_t idx = (125 - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm(A_125_soft, &ticks);

        data = Calc(idx, ticks);

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        /* Post Hook */
        TerminateTask();
}
        
