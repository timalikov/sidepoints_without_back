import os
from dotenv import load_dotenv

load_dotenv()


MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
RU_GUILDS = [773446008053956650]
GUILDS_FOR_TASKS = [*RU_GUILDS, MAIN_GUILD_ID]

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PORT_ID = int(os.getenv('PORT_ID'))
FORUM_ID_LIST = [1237300150301360138, 1244598037758738553]
CUSTOMER_SUPPORT_TEAM_IDS = [713830377189277845, 1050451653070950503, 585751002167115806, 412607075622060032, 1255068242469326928, 1120088026828242976, 517856669338959881, 388031483924840460, 419205987895869440, 11728720708042834, 1172872070804283405]
TEST=os.getenv('TEST')
SUPER_KICKER_IDS = [
    1114614606128758905,
    791593422443380746,
    713830377189277845,
    969254956236439576,
    1266407300621406262,
    490286834262474752,
    1258498409002959012,
    402439815360020491,
    865273967093481512,
    910723966434414613,
    520191900112650240,
    517856669338959881,
    988852690673082438,
    945831155498909706,
    1118045871490215996,
    794680426383278101,
    1066111649909584025,
    928934711319986206,
    1092908429032554517,
    920087530701991987,
    817651476092026882,
    1023013457634807838,
    852549260851675156,
    1036053462665932810,
    570147064315379713,
    894115303766765599,
    667375351394992150,
    824225621961867336
]
TEAM_CHANNEL_ID = 1283327337777074177

# link_to_back = f"http://127.0.0.1:8001/discordServices"
link_to_back = os.getenv('BOTAPI_URL') # f"http://172.31.7.179:8001/discordServices"

SERVER_ID_LIST = []

LEADER_BOT_CHANNEL_LIST = [1242448780801081475, 1240912296981561405, 1242449117461086290]

APP_CHOICES = {
    "BUDDY": "57c86488-8935-4a13-bae0-5ca8783e205d",
    "COACHING": "88169d78-85b4-4fa3-8298-3df020f13a6f",
    "JUST_CHATTING": "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360",
    "MOBILE": "439d8a72-8b8b-4a56-bb32-32c6e5d918ec",
    "Watch Youtube": "d3ae39d2-fd86-41d7-bc38-0b582ce338b5",
    "Play Games": "79bf303a-318b-4815-bd56-7b0b49ae7bff",
    "Virtual Date": "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"
}

TASK_DESCRIPTIONS = {
    "57c86488-8935-4a13-bae0-5ca8783e205d": "BUDDY",
    "88169d78-85b4-4fa3-8298-3df020f13a6f": "COACHING",
    "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360": "JUST_CHATTING",
    "439d8a72-8b8b-4a56-bb32-32c6e5d918ec": "MOBILE",
    "d3ae39d2-fd86-41d7-bc38-0b582ce338b5": "Watch Youtube",
    "79bf303a-318b-4815-bd56-7b0b49ae7bff": "Play Games",
    "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9": "Virtual Date"
}

CATEGORY_TO_TAG = {
    "57c86488-8935-4a13-bae0-5ca8783e205d": "BUDDY",
    "88169d78-85b4-4fa3-8298-3df020f13a6f": "COACHING",
    "2974b0e8-69de-4d7c-aa4d-d5aa8e05d360": "JUST CHATTING",
    "439d8a72-8b8b-4a56-bb32-32c6e5d918ec": "MOBILE",
    "d3ae39d2-fd86-41d7-bc38-0b582ce338b5": "Watch Youtube",
    "79bf303a-318b-4815-bd56-7b0b49ae7bff": "Play Games",
    "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9": "Virtual Date"
}

MESSAGES = [
    (10, "🚀 Just a quick update: We're on it! Thanks for your patience! 🌟 Kicker should join within 5 minutes, otherwise we will refund your money.", False),
    (20, "🔧 Our team is working their magic! Hang tight - we're almost there! Kicker should join within 4 minutes 40 seconds, otherwise we will refund your money.", False),
    (40, "⏳ Thanks for sticking with us! We’re making progress, stay tuned! 🚀 Kicker should join within 4 minutes 20 seconds, otherwise we will refund your money.", False),
    (60, "", True), 
    (80, "💪 We’re on a mission to get this sorted for you! Thanks for your patience! 🙌 Kicker should join within 3 minutes 40 seconds, otherwise we will refund your money.", False),
    (110, "🛠️ Almost there! Our team is busy behind the scenes. We appreciate your patience! 🎉 Kicker should join within 3 minutes 10 seconds, otherwise we will refund your money.", False),
    (150, "🎯 We’re making strides! Thanks for hanging in there – we’ll be with you shortly! 🚀 Kicker should join within 2 minutes 30 seconds, otherwise we will refund your money.", False),
    (180, "", True),
    (210, "✨ Just a little bit more time! We’re working hard to get everything sorted. Thanks! 💪 Kicker should join within 1 minute 30 seconds, otherwise we will refund your money.", False),
    (240, "🔍 Almost ready! Our team is doing their thing. Thanks for waiting! 🙌 Kicker should join within 1 minute, otherwise we will refund your money.", False),
    (255, "Oops! Looks like we hit a snag. We're on it and will make it right soon! 🙌 Kicker should join within 45 seconds, otherwise we will refund your money.", False),
    (270, "Oops! 😬 We hit a snag and couldn’t deliver. No worries – get your refund 💸 <#1233350206280437760>. Thanks for your patience! Kicker should join within 30 seconds, otherwise we will refund your money.", False),
    (285, "My bad! 🙊 We missed the delivery. Click  <#1233350206280437760> to grab your refund 💵 and we’ll get things sorted out. Thanks for sticking with us! Kicker should join within 15 seconds, otherwise we will refund your money.", False),
    (300, "Our bad! We couldn’t get it to you on time. Expect a refund soon, and we’ll make sure it doesn’t happen again! Click here <#1233350206280437760> to refund.", False)
]

HOST_PSQL = os.getenv('HOST_PSQL').strip()
USER_PSQL = os.getenv('USER_AWS_PSQL').strip()
PASSWORD_PSQL = os.getenv('PASSWORD_PSQL').strip()
DATABASE_PSQL = os.getenv('DATABASE_PSQL').strip()
PORT_PSQL = os.getenv('PORT_PSQL').strip()

BOOST_CHANNEL_ID = 1285193246183784488
ORDER_CHANNEL_ID = 1284079837941731379

ORDER_CATEGORY_NAME = "Kickers"
ORDER_CHANNEL_NAME = "🔔order-dispatch"

FIRST_LIMIT_CHECK_MINUTES = 5
SECOND_LIMIT_CHECK_MINUTES = 30

FORUM_NAME = "🔎find-your-kickers"
FORUM_CATEGORY_NAME = "Sidekick: Match to Play"

LINK_LEADERBOARD = "https://app.sidekick.fans/leaderboard/points"
LEADERBOARD_CHANNEL_NAME = "🏆sidekick-leaderboards"
LEADERBOARD_CATEGORY_NAME = "Community 😎"

TEST_ACCOUNTS = [
    944953902015590410,
    958598106197405736,
    943418355979784242,
    937126463436636200,
    945024024067604520,
    1240378234571456562,
    1240471906856079360,
    1233411070207721494,
    959991016549675058,
    1240073274289815655,
    1257154521088528415,
    1265790904631820379,
    1265792801686163633,
    958322734847385600,
    958672553960951818,
    960003611579011132,
    959979850557444146,
    958651161504788554,
    958587574451077151,
    1256946877988077720,
    1265792807290011690,
    1265792809169063988,
    1255896294736527400,
    944941852845551626,
    937226670237159476,
    958641593341067264,
    937194605391265842,
    959776574394212373,
    943791370206842880,
    1257161252288073809,
    1267232150923513969,
    1257852703493718098,
    1257414547828900031,
    958496906831593507,
    959815209155964998,
    958638639364055082,
    1024820273448493106,
    936349956443344938,
    943802563785023498,
    944958997604212838,
    959791328705806356,
    959802734138241034,
    959806831839027230,
    943798008775073833,
    943972474444451860,
    958609558786428929,
    937341020704755733,
    945024505150050416,
    958588248047890492,
    959268377803763712,
    943799329632686110,
    937159220577570847,
    959948267653840987,
    958727965573783574,
    937230627063877662,
    959951543749181490,
    958595488322572348,
    945037981729837067,
    959814874463092816,
    945028223329263677,
    944955709915803698,
    959958984754864200,
    936666389706584105,
    945034519143129119,
    936746179805466625,
    958592844233338951,
    960003342657015858,
    943283816468987905,
    945370732295225355,
    957852792742109244,
    937096428055060532,
    959964946609881088,
    934888083718021131,
    958518990802681896,
    958499657540075572,
    934964296549552209,
    958676144083857488,
    944927893417508904,
    958629670692204585,
    958623983379566683,
    944091768708812812,
    958338922809810994,
    945030896636006471,
    945086600914804786,
    937210511261573120,
    958498842033152000,
    944093853827342426,
    958642067049943100,
    943347813562064906,
    934890426362646600,
    959949541589778492,
    951926255912112168,
    958501391087841281,
    959271119523827754,
    958500105172947004,
    944940836561494067,
    937339343075426375,
    958606740163809300,
    959949813078695936,
    958590737333755964,
    958542808057253959,
    943394175381016586,
    937339209700769792,
    937242382007668736,
    968247071079538750,
    958597871064719406,
    958662946941177921,
    957870278959050752,
    932624844682571847,
    959837461784166521,
    943588356930035772,
    960000903358865478,
    943587204301738115,
    958324851054092359,
    944924769189515295,
    958611435691327528,
    959321659901349958,
    944938865012129833,
    943734908998795264,
    959806683893342259,
    937341049234411560,
    958501362889551902,
    944954719544156160,
    958628813661679617,
    959223494753804398,
    960012948141662219,
    945174726052028427,
    945023534571352064,
    959264009075425331,
    958583737900220446,
    959956260709597235,
    943798873900589086,
    958644819729723463,
    958683518865645599,
    958509659617116190,
    958629871570001930,
    958540518021808158,
    959818448224002062,
    936754871972012073,
    958335595577487430,
    959834717476233347,
    959798403305439234,
    958741196967129108,
    943799841773985852,
    957883338167828501,
    960021168058925096,
    959976609677475930,
    935849262296756235,
    959259249991622737,
    958588654492745758,
    959776668199845898,
    958608877253984286,
    959792719591505961,
    937219876274196560, 
    944947887119413278,
    957785228196335636,
    960045246392188938,
    958546928629612624,
    945100800621944882,
    943545337598079086,
    959221906207309864,
    958608127304011778, 
    943298643614634085,
    959795573014298655,
    943798549437628416,
    958627715974570034,
    958499510080917516,
    944949965560614932,
    958629258262118440,   
    937212533520101386,
    958588157899706368,
    943793588591022101,
    958570210816835584,
    944960865185177611,
    944272419361812530,
    958511308561608745, 
    960012090658140160,
    959828789884485652,
    936390668601917500,
    958565453855354900,
    958671366020821002,
    958678416587128852,
    943776418746224680,
    959967894899404861,
    957763295153098792,
    959825518767771678,
    959178707870822490, 
    958505532795260998,
    944093417368088689,
    958536200854057080,
    936660814893551626,
    954574191057829939,
    943746494643703858,
    945022913881440337,
    944273061715267604,
    958657407314186323,
    943800802428997663,
    959254203480543242,
    937158611619180554,
    958487863257882634,
    959955161118285834,
    934781903108718592,
    957738552052023336,
    951848025981063258,
    957583398325612564,
    957752442395701258,
    932619662653542420,
    957671781295095840,
    934938000889102347,
    934884764828192818,
    946338401643286539,
    957721088534646814,
    934821603148197928,
    934512892248739892,
    957654584413794394,
    957649771747737680,
    957656128437751878,
    934843016424857631,
    951869223280476160,
    935178305571803166,
    957717549745844234,
    946485869676732416,
    936661485206265877,
    946462697774538902,
    951865925395689564,
    951910290897907762,
    957712735439835156,
    946340462812356628,
    940959823481163798,
    946495114459627610,
    957687824545636353,  
    957756797740019783,
    954598195168677898,
    957655238947532810,
    951915987962331216,
    1022907468935860365,
    934816258417909820,
    957663211417632788,
    957667280127397958,
    956219150324367361,
    951869060809916497,
    954407042129477673,
    957661553887424572,
    934780827122929735,
    934458469182996621,
    957722756588371968,
    934784559822807040,
    932452405495345202,
    957722530024669314,
    936674130923782245,
    951925455437574197,
    957655750463868939,
    946338318583496724,
    959801873634820227,
    957617003181506610,
    959963031213838376,
    958571634812407810,
    959783689963835432,
    958577522931556422,
    958607944189104198,
    959762488042336256,
    959818266333831259,
    959251262044524624,
    957845211172724796,
    958683793915523102,
    959958526145486908,
    959313377887420497,
    958531456974594059,
    944093774886363177,
    937350882398470174,
    959241032019615764,
    943627757038997584,
    959996453474947092,
    959987331044102145,
    958666970453127228,
    943546301491077120,
    959962697779257365,
    935849393834307694,
    957898930509709322,
    958516165834063902,
    958605418710593546,
    958750699116716152,
    958341785493569546,
    958669425358282762,
    958668844220702780,
    958661359728459777,
    957889053695569920,
    943341343630049370,
    959783037304963082,
    957822442909352036,
    958485782778216489,
    958635981408444478,
    957914302239617024,
    960008110167191642,
    957893164574851106,
    958500489111142420,
    959778478130102272,
    958486824127434783,
    935845718038564894,
    958594463075287050,
    959769767881879625,
    960017859944280115,
    959799326463369226,
    968259951497736373,
    959993974616113183,
    959985706334310490,
    958554761718800436,
    944934331149864991,
    958753437519073280,
    958659982360977418,
    959797686788296744,
    937347266052780052,
    958644461682958347,
    958665152004247602,
    958576913574674433,
    958516199942160484,
    944939847737569320,
    958807956760174642,
    958663340387864616,
    944742089520992307,
    937338959695065108,
    958584342790144000,
    960007873201586186,
    943800346608812062,
    959956116018724964,
    959171600199057499,
    937939088999329793,
    957822341512060938,
    959762508460220476,
    968258677071048785,
    943393856429367297,
    958532161642831942,
    959992412753784923,
    936674411799515188,
    958496934732136458,
    944941574314414130,
    958597048758849587,
    959264838973009930,
    958563237664784435,
    959815326739103814,
    945027160983363674,
    958321367856599080,
    957815668407947364,
    958639674841268264,
    959951754231955516,
    958630965683560448,
    959775247752630362,
    968243617711939594,
    943744025574379530,
    959227616215330836,
    958568121717891083,
    960037889977245746,
    936390440456949840,
    959985790153265182,
    944955283514482748,
]