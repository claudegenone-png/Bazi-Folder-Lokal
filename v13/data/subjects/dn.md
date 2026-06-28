# DN
# ============================================================
# V11 MD BLUEPRINT — copy file ini, isi dari foto, tulis null kalau tidak terlihat
# JANGAN ubah key name. JANGAN hapus key. JANGAN guess nilai — null kalau tidak ada.
# xi_yong_shen = 喜神 (BUKAN xi_shen — xi_shen tidak diparse engine)
# dm_pos_score / dm_neg_score = INTEGER e.g. 4100 (bukan +4.100)
# liu_nian_YYYY = umur|ganzhi|prose (WAJIB dua pipe, e.g. 24|丙午|Tekanan tahun...)
# yang_zhai_gua WAJIB ada kalau ada foto 陽宅 (e.g. 艮/坤/震/巽/離/坎/兌/乾)
# jie_e_palace_id WAJIB di ## DATA flat key — TAFSIR jie_e.insight tidak cukup
# ============================================================

## DATA

# === Identity ===
- nama: DN
- hanzi: null
- gender_hz: 陽男
- gender: Pria
- shio_hz: 猴
- lahir_tanggal_lunar: 農曆庚申民國69年1月26日
- lahir_tanggal: 1980-03-12
- lahir_jam: 08:10
- pilar_tahun: 庚/申
- pilar_bulan: 己/卯
- pilar_hari: 甲/申
- pilar_jam: 戊/辰

# === 先天體檢 (organ scores, integer 0-3) ===
- xiantian_jia: 1
- xiantian_yi: 2
- xiantian_bing: 0
- xiantian_ding: 0
- xiantian_wu: 4
- xiantian_ji: 1
- xiantian_geng: 3
- xiantian_xin: 0
- xiantian_ren: 2
- xiantian_gui: 1

# === 喜用神 5-shen panel (dari foto — posisi atas ke bawah) ===
- yong_shen: 火
- xi_yong_shen: 水
- xian_shen: 木
- chou_shen: 土
- ji_shen: 金

# === 格局 Format ===
- format: 比肩格

# === DM Strength ===
- dm_pos_score: 3560
- dm_neg_score: 4900

# === 大運 Da Yun ===
- da_yun_arah: 順行
- da_yun_start_age: 8
- da_yun: 8:庚辰:七殺, 18:辛巳:正官, 28:壬午:偏印, 38:癸未:正印, 48:甲申:比肩, 58:乙酉:劫財, 68:丙戌:食神, 78:丁亥:傷官, 88:戊子:偏財, 98:己丑:正財

# === 婚配 Marriage ===
- marriage_cocok_shio_hz: 鼠, 龍
- marriage_hindari_shio_hz: 虎, 蛇, 豬
- marriage_cocok_tafsir: Bak permata yang saling melengkapi [[珠聯璧合]], perjalanan kehidupan bersama akan berjalan mulus dan lancar. Tidak ada halangan yang berarti — kesuksesan dan kemakmuran [[成功富貴]] akan hadir, keturunan berkembang pesat, dan kemakmuran keluarga berlanjut selama lima generasi [[五世其昌]].
- marriage_hindari_tafsir: Pada awal kehidupan bersama, berbagai bencana dan kesulitan datang silih berganti. Menjelang usia tua barulah kebahagiaan hadir bersama. Di pertengahan perjalanan, mungkin terjadi kesulitan besar atau musibah [[災殃]], atau kehilangan sandaran orang tua sejak masih muda [[少小怙恃]], atau umur yang tidak panjang [[壽不永]] — malapetaka [[災難]] dan penyakit yang menyengsarakan [[病疾困苦]] dapat menghampiri.
- marriage_cocok_relationships: 子:大吉, 辰:大吉

# === 陽宅 Yang Zhai ===
- yang_zhai_gua: 坤
- yang_zhai_zone_rumah_hz: 東北, 西南
- yang_zhai_zone_rumah_note: Rumah sangat baik bila duduk di timur laut menghadap barat daya, atau duduk di barat daya menghadap timur laut.
- yang_zhai_zone_pintu_hz: 西, 西北
- yang_zhai_zone_pintu_note: Pintu atau jalur masuk baik dibuka di sektor barat atau barat laut.
- yang_zhai_zone_dapur_hz: 東
- yang_zhai_zone_dapur_note: Kompor baik ditempatkan di timur dengan arah menghadap barat.
- yang_zhai_zone_kamar_hz: 西, 西北, 西南, 東北
- yang_zhai_zone_kamar_note: Kamar baik ditempatkan di sektor barat, barat laut, barat daya, atau timur laut.
- yang_zhai_zone_ranjang_hz: 西, 西南, 東北, 西北
- yang_zhai_zone_ranjang_note: Posisi ranjang baik berada di sektor barat, barat daya, timur laut, atau barat laut.
- yang_zhai_zone_altar_hz: 西, 西北, 西南, 東北
- yang_zhai_zone_altar_note: Altar baik ditempatkan di sektor barat, barat laut, barat daya, timur laut, atau arah keberuntungan utama pada tahun berjalan.
- yang_zhai_zone_kamar_mandi_hz: 北, 東, 東南, 南
- yang_zhai_zone_kamar_mandi_note: Toilet atau kamar mandi baik ditempatkan di sektor utara, timur, tenggara, atau selatan.

# === 紫微 Zi Wei ===
- ziwei_ming_zhu: 祿存
- ziwei_shen_zhu: 天梁
- ziwei_ming_gong: 戌
- ziwei_shen_gong: 午
- ziwei_wu_xing_ju: 土五局
- ziwei_shi_jun: 辰
- ziwei_su_ming: Baik atau buruknya perjalanan hidup dipandang sebagai bagian dari ketetapan nasib. Selama kekuatan istana keuangan baik, istana tubuh juga menjadi kuat. Dengan dukungan keberuntungan finansial, DN dapat menjalani hidup tanpa terlalu mencemaskan kelapangan uang. Sebaliknya, bila istana keuangan lemah, ia dapat bekerja keras sepanjang hidup demi uang dan justru dipermainkan oleh urusan keuangan. Dalam menilai keadaan tersebut, kekuatan istana diri Ming Gong [[命宮]], istana kebahagiaan Fu De Gong [[福德宮]], dan istana karier Guan Lu Gong [[官祿宮]] juga harus dipertimbangkan bersama.

# === 適業 Career ===
- ziwei_career_recommended_hz: 火熱光性工廠或物品、照相、電器、光學、眼鏡、熱飲小吃、食品工廠、燙髮美容、衣帽百貨、評論家、化妝品、軍界、煙酒
- ziwei_career_recommended_id: Pabrik atau produk yang berkaitan dengan panas, api, dan cahaya; fotografi; peralatan listrik; optik; kacamata; minuman panas dan makanan ringan; pabrik makanan; tata rambut dan kecantikan; toko pakaian, topi, atau serba ada; kritikus; kosmetik; bidang militer; serta usaha rokok dan minuman beralkohol.
- ziwei_career_alternate_hz: null
- ziwei_career_alternate_id: null
- shiye_favorable_full: 火熱光性工廠或物品|Pabrik atau produk panas, api, dan cahaya, 照相|Fotografi, 電器|Peralatan listrik, 光學|Optik, 眼鏡|Kacamata, 熱飲小吃|Minuman panas dan makanan ringan, 食品工廠|Pabrik makanan, 燙髮美容|Tata rambut dan kecantikan, 衣帽百貨|Toko pakaian, topi, atau serba ada, 評論家|Kritikus, 化妝品|Kosmetik, 軍界|Bidang militer, 煙酒|Usaha rokok dan minuman beralkohol
- shiye_supportive_full: 流動攤販|Pedagang keliling, 運動家|Atlet, 介紹中人|Perantara, 醫師|Dokter, 清潔隊|Petugas kebersihan, 記者|Jurnalis, 護士|Perawat, 導遊|Pemandu wisata, 馬戲團|Sirkus, 航海|Pelayaran, 漁業|Perikanan, 水產業|Industri hasil perairan, 碼頭工|Pekerja dermaga, 消防隊|Pemadam kebakaran, 貿易公司|Perusahaan perdagangan

# === 命宮 Ming Gong ===
- palace_ming_gong_insight: DN adalah sosok yang meski memiliki kelemahan sifat lamban dan suka bertele-tele [[拖泥帶水]], namun perjalanan hidupnya tetap cerah dan kokoh. Postur tubuhnya relatif tinggi [[身材較高]], lebih kekar dan sehat dibandingkan orang kebanyakan. Ciri khas utamanya adalah sikap yang hangat dan mudah bergaul dengan siapa pun [[和藹可親]], disertai kemampuan berpikir yang sangat cepat dan tajam. Karakternya lembut dan bersahabat [[性格溫馴待人和氣]], kaya akan keluwesan dan fleksibilitas [[柔軟性]] — namun di sisi lain, ia juga memiliki sisi keras kepala [[執拗]] dan gemar turut campur urusan orang lain. Apapun urusan orang lain, selama ia bersinggungan dengannya, ia pasti akan ikut terlibat. Justru karena naluri bawaan yang gemar membantu ini, bahkan tanpa diminta sekalipun, ia dengan antusias akan mengulurkan tangan [[熱心地幫助]] — sehingga ia memiliki banyak teman, dan dihormati oleh mereka yang lebih muda sebagai kakak tertua yang bisa diandalkan [[足可信賴的老大哥]]. Namun, mereka yang lebih tua cenderung memandangnya sebagai orang yang suka ikut campur urusan orang lain. Bagi perempuan dengan bintang istana kehidupan ini, umumnya termasuk dalam kelompok perempuan berbakat [[才女之流]] yang kemampuannya tak kalah dari kaum pria, bahkan bisa melampaui mereka. Dalam hal apapun, selalu ingin bersaing dan membuktikan diri. Setelah menikah, akan menjadi istri yang cakap sekaligus pemimpin yang tegas [[能幹妻子]], bahkan mampu mengambil alih peran kepemimpinan dari suami. Yang perlu diperhatikan adalah jangan terlalu berlebihan dalam mencampuri urusan pasangan. DN memiliki karakter yang lurus, jujur, dan berjiwa besar [[豪爽正直]], mampu berdiri di atas orang lain dan menempati posisi kepemimpinan [[領導地位]]. Dengan sifat yang terbuka dan teratur dalam bertindak [[爽朗行事也有節制]], ia mudah mendapat kepercayaan dari banyak pihak. Dalam setiap kegiatan kelompok, ia pasti akan menempati posisi pemimpin dan menjadi figur inti [[核心人物]] yang diandalkan oleh komunitas. Apabila bintang Tianji [[天機星]] berada dalam satu istana yang sama, bakat sastra dan kecerdasan intelektual [[文才]] dapat mengantarkannya pada ketenaran, sekaligus mendatangkan keberuntungan finansial. Bagi kaum perempuan dengan konfigurasi ini, sifat yang terlalu maskulin akibat kepribadian yang terlalu bersemangat justru membuat kesan pertama kurang mendalam. Sejak kecil sering bermain bersama anak laki-laki, sehingga kepribadiannya cenderung sedikit ceroboh [[輕佻]] dan tidak terlalu feminin. Namun demikian, mereka yang benar-benar mengenal kejujuran dan ketulusan hatimu [[腸子不虛偽]] pasti akan menaruh kepercayaan yang mendalam padamu. Yang perlu kamu perhatikan hanyalah menjadi sedikit lebih lembut dalam bersikap — dan itu sudah lebih dari cukup.

# === 疾厄 Jie E ===
- jie_e_palace_id: DN cenderung mudah mengalami gangguan tenggorokan, flu, sakit gigi, dan keluhan sejenis. Secara umum ia jarang terserang penyakit atau cedera; bila sakit, pemulihan melalui pengobatan juga cenderung berlangsung cepat. Bila berada bersama bintang yang kurang baik, ia lebih mudah mengalami gangguan lambung, beri-beri, atau keluhan sejenis. Bila berada bersama bintang Kaisar Ungu Zi Wei [[紫微]], kondisi kesehatannya sangat baik dan tidak perlu terlalu mencemaskan penyakit.
- jie_e_organ_focus_id: Tenggorokan, gigi, lambung, dan sirkulasi atau saraf kaki.

# === 神煞 Shen Sha ===
- shen_sha_detail_1: 華蓋|Hua Gai|Kanopi Kemuliaan|求學能自動，自悟以達最高學歷，天性對美術、設計、裝潢、音樂、文學方面大興趣及天才。|DN mempunyai dorongan belajar mandiri dan kemampuan memahami sesuatu melalui perenungan sendiri hingga berpotensi mencapai pendidikan tinggi. Secara alami ia memiliki minat besar dan bakat dalam seni rupa, desain, dekorasi, musik, serta sastra.
- shen_sha_detail_2: 元辰大耗|Yuan Chen Da Hao|Kehilangan Besar Yuan Chen|手腳強硬，不別是非，寒酸，貪飲好情，逞雄性獨，不遵禮法，一生多災。|DN dapat bertindak keras, kurang membedakan benar dan salah ketika dorongan pribadinya menguat, bersikap kaku atau terlalu perhitungan, menyukai minuman dan urusan perasaan, ingin menonjolkan kekuatan secara sendiri, serta kurang memedulikan tata krama. Pola ini perlu dikendalikan karena dapat mendatangkan banyak kesulitan sepanjang hidup.
- shen_sha_detail_3: null
- shen_sha_detail_4: null

# === 流年 Liu Nian ===
- liu_nian_2026: 47|丙午|Tahun 2026 membuka peluang bagi DN untuk mengubah kecerdikan dan gagasan menjadi hasil yang bernilai. Ia mampu memakai pikirannya untuk menemukan jalan bagi berbagai urusan, sehingga perlu menangkap kesempatan, lebih banyak menggunakan daya pikir, dan dengan itu dapat mencapai hasil ideal. Tanda Diao Ke menyebut rangkaian urusan duka, kemungkinan perkara hukum atau gangguan yang berkaitan dengan darah, serta kabar dukacita yang menyentuh anggota keluarga lebih muda. Namun, bintang kebajikan Yang De membawa peluang peristiwa menggembirakan, kehormatan bagi rumah, dan perayaan yang berjalan tanpa masalah; dengan menumpuk kebajikan dan melakukan kebaikan, urusan dapat berlangsung lancar. Perhatian khusus diperlukan pada bulan pertama, keempat, kesepuluh, atau kesebelas; kebaikan perlu dilakukan dengan tulus dan pertengkaran harus dihindari. DN juga perlu lebih waspada agar tidak dijebak orang lain, tidak mengalami perubahan lingkungan atau pekerjaan yang merugikan, dan tidak terseret perselisihan, ucapan yang menimbulkan perkara, gugatan hukum, penahanan, atau cedera. Pada tahun ini sifatnya lebih mudah terburu-buru dan kemampuan memutuskan dapat melemah, sehingga ia ragu-ragu meskipun sangat cerdas. Kecenderungan memikirkan persoalan terlalu sempit dapat menimbulkan beban dan gangguan yang sebenarnya tidak perlu. Hubungan suami istri juga cenderung tipis dan mudah berubah, sehingga menjaga komunikasi dan komitmen menjadi penting; sumber bahkan menyebut kecenderungan pernikahan ulang lebih banyak muncul pada pola ini.
- liu_nian_2027: 48|丁未|Tahun 2027 mempertemukan potensi finansial dari pemikiran DN dengan kebutuhan menjaga tubuh dan kestabilan batin. Datangnya rezeki dapat disertai masalah, dan hasil nyata belum tentu mencapai keadaan ideal. Situasi tahun ini menekan perasaan sehingga suasana hati juga kurang stabil. Tanda Bing Fu menunjukkan kemungkinan penyakit, persoalan resmi, kemunduran, atau urusan duka, sehingga sumber menyarankan memohon perlindungan spiritual. Di sisi lain, bintang Jin Xiu membawa peristiwa gembira, rumah yang ramai oleh tamu, peluang memperoleh keturunan sesuai harapan, dan keberuntungan yang masuk ke keluarga. DN perlu mewaspadai perkara resmi pada bulan ketiga, keenam, kesembilan, atau kedua belas. Selama seluruh keluarga memperhatikan perubahan cuaca dan menghindari penularan penyakit, keadaan dapat berjalan tanpa masalah besar. Pada tahun ini sifat tertutup, kebiasaan yang agak tidak lazim, dan kurangnya minat menghias penampilan dapat lebih terlihat. Hubungan dengan saudara kandung cenderung tipis. DN juga menyukai pengumpulan benda kecil dan termasuk orang yang ingin menabung dengan sungguh-sungguh. Ia dianjurkan membuka hati dan bergerak maju dengan tekun agar keberuntungan keuangan dapat menjadi baik. Pola hidup yang lebih berat dan penuh kesulitan pada paruh pertama kehidupan dapat berbalik menjadi semakin beruntung dan nyaman pada paruh kedua.
- liu_nian_2028: 49|戊申|Tahun 2028 menjadi fase perubahan besar yang menuntut lebih banyak tenaga daripada imbalan yang langsung terlihat. DN perlu mewaspadai penyakit kronis dan pengeluaran yang sangat besar, sementara hasil nyata sulit mencapai keadaan ideal. Usaha atau kedudukan kerja dapat mengalami perubahan. Lingkungan besar juga berubah, misalnya rumah direnovasi kembali, pindah tempat tinggal, atau memindahkan perabot dan tata ruang. Bagi yang telah menikah, hubungan suami istri mudah mengalami gejolak perasaan; bagi yang belum menikah, perjalanan hubungan cinta menjadi lebih aktif. Tanda Tai Sui menyebut tekanan berada tepat di hadapan, tetapi bila tubuh tidak mengalami benturan berat, tahun ini masih dapat dipakai untuk merencanakan dan menjalankan urusan dengan baik. Tanda Tian Ku membawa risiko penyakit dan urusan duka; bila istri atau keluarga mengalami peristiwa kelahiran yang menggembirakan, tekanan dapat bergeser menjadi pertengkaran lisan tanpa bencana yang lebih berat. Bulan kedua, ketiga, kelima, atau kesebelas perlu diwaspadai. Sumber juga menyarankan penghormatan kepada Tai Sui pada tanggal sembilan bulan pertama lunar untuk memohon keselamatan. Arah baik dan buruk tahun ini cenderung ekstrem. DN menjadi lebih mudah terburu-buru, cepat bersemangat tetapi juga cepat berhenti, memulai tanpa menuntaskan, serta menyukai hal baru dan mudah bosan terhadap yang lama. Dorongan spontan dan kurangnya pemikiran jauh dapat membuatnya ringan dalam bertindak, mudah ditipu, terlena oleh keberhasilan, dan gagal karena langkah yang gegabah. Walaupun perjalanan tahun ini tidak tenang, ia tetap mempunyai peluang menemukan jalan hidup ketika keadaan sudah berada di titik paling sulit.
- liu_nian_2029: 50|己酉|Tahun 2029 menguji kemampuan DN menjaga keseimbangan antara tenaga yang dicurahkan, pengeluaran, dan hasil yang diterima. Ia perlu mewaspadai penyakit kronis dan pengeluaran yang sangat besar, sedangkan hasil nyata sulit mencapai keadaan ideal. Suasana hati relatif tidak stabil. Usaha atau kedudukan kerja juga dapat mengalami perubahan. Bintang Matahari Tai Yang membawa keharmonisan dalam berbagai urusan, keseimbangan yang tidak melenceng, berkah, dan peluang memperoleh harta. Bintang Fu De yang masuk ke perjalanan tahunan menunjukkan akhlak yang baik, dukungan orang lain dalam mencari rezeki dan urusan gembira, serta masa kemudian yang lebih baik daripada perjalanan sebelumnya. Bulan kedua, keempat, kedelapan, atau kesebelas perlu diwaspadai. Bagi orang yang sebelumnya sakit atau sedang bernasib kurang baik, tahun ini memberi isyarat adanya perbaikan. Rasa ingin tahu dan semangat penelitian DN menjadi kuat. Ia memiliki jiwa yang terus memperbarui diri, menyukai kesegaran, kreatif, penuh humor, dan mempunyai kehangatan kemanusiaan. Sifatnya termasuk cerdas tetapi tidak selalu mempertontonkan kecerdasan tersebut, dan keberuntungan cukup sering mendatanginya. Tubuhnya tidak selalu berada dalam kondisi sehat, tetapi semakin bertambah usia justru dapat semakin kuat. Bagi wanita dengan pola ini, kemungkinan melahirkan anak perempuan dinilai lebih tinggi.
- liu_nian_2030: 51|庚戌|Tahun 2030 membawa tekanan yang lebih berat, arus pengeluaran yang membesar, dan perubahan yang perlu dihadapi dengan tenang. Kondisi tubuh perlu diperhatikan. Datangnya rezeki juga dapat disertai masalah, sementara hasil nyata belum tentu mencapai keadaan ideal. Usaha atau pekerjaan dapat mengalami perubahan. Keadaan tahun ini menekan perasaan sehingga suasana hati pun kurang stabil. Tanda Sang Men menunjukkan urusan duka, benturan atau gangguan, kerusakan, pengeluaran, dan kehilangan harta. Tanda Hei Sha menyebut perjalanan yang terbalik atau mengejutkan; bila tidak ada benturan berat, urusan duka tetap perlu diwaspadai, demikian pula gangguan pencuri atau orang yang berniat buruk. Peristiwa menggembirakan dalam keluarga dapat membantu menjaga keselamatan. Bulan keenam, kedelapan, atau kesebelas perlu diwaspadai, dan sumber menyarankan memelihara hati yang baik untuk mengundang berkah. Pada tahun ini DN tidak disarankan menjenguk orang yang sakit berat atau menghadiri urusan pemakaman agar tidak menarik kemerosotan, dan terdapat kemungkinan kerabat atau teman mengalami penyakit berat atau meninggal. Sifatnya cenderung jujur dan bersahaja, serta cukup terampil dalam pergaulan, tetapi tidak selalu mempunyai ambisi besar dan lebih mudah merasa cukup dengan keadaan sekarang. Hubungan dengan orang tua kandung relatif tipis; pola ini juga dikaitkan dengan kemungkinan diasuh keluarga lain atau masuk ke keluarga pasangan. Walaupun demikian, selama DN tetap berusaha maju, ia masih dapat mencapai keberhasilan yang tinggi dan besar.
- liu_nian_2031: 52|辛亥|Tahun 2031 menghadirkan dukungan dari orang yang lebih tua dan para pembimbing, sehingga peluang mencapai hasil ideal menjadi lebih terbuka. Meskipun demikian, tekanan tahun ini cukup berat dan pengeluaran besar, sehingga gangguan tubuh perlu diperhatikan. Keadaan juga menahan perasaan dan membuat suasana hati kurang stabil. Bintang Tai Yin membawa peristiwa menggembirakan, perolehan harta, bantuan orang berpengaruh, dan keharmonisan dalam banyak urusan. Bintang Wen Chang yang masuk ke perjalanan tahunan membawa kabar bahagia ke rumah; pelajar atau orang yang mengejar prestasi dapat memperoleh hasil baik, masyarakat umum memperoleh peluang rezeki, dan wanita dapat menerima kabar kehamilan. Bulan kedua, kelima, kedelapan, atau kedua belas perlu diwaspadai. DN juga dapat menarik rasa tidak suka atau gejolak dari lawan jenis dan sebaiknya tidak berjalan di tempat gelap pada larut malam. Sifat jujur, lembut, sopan, baik, dan matang menjadi lebih menonjol. Hubungan sosialnya sangat baik sehingga ia mudah dihargai, diterima, disukai, dan diangkat oleh orang lain, serta berpeluang naik dengan cepat. Ia mempunyai bakat teknik dan seni serta kemampuan belajar yang kuat. Namun, sumber menilai bahwa ia kurang sesuai memegang lapisan kepemimpinan tertinggi; kemampuannya justru sangat baik ketika berperan sebagai pendamping utama, perencana, atau staf strategis, karena di posisi tersebut ruang untuk memperlihatkan kemampuan menjadi lebih luas.

# === 古書云 ===
- gushu_quote_1: Catatan San Ming Tong Hui menyatakan bahwa Kayu Jia dan Yi pada musim semi berada dalam keadaan yang sesuai; keistimewaannya terlihat ketika Logam dan Air kuat. Pada musim semi bergerak ke selatan, pada musim gugur kembali ke utara, sedangkan perjalanan ke barat pada musim dingin dan musim panas menjadi dasar tumbuhnya keberuntungan. Dalam gambaran Naga Hijau Tersembunyi, bila Jia dan Yi berada di wilayah Monyet Shen dan Ayam You, Kayu yang bertemu kemakmuran musim semi menjadi paling baik; bila empat pilar juga mendapat bantuan gudang unsur, kekayaan dan kedudukan resmi sama-sama indah serta melampaui keadaan biasa. Di Tian Sui disebutkan bahwa Kayu Jia menjulang ke langit dan untuk melepaskan bentuk awalnya memerlukan Api; pada musim semi tidak menerima Logam, pada musim gugur tidak menerima Tanah; ketika Api menyala ia menunggang Naga, ketika Air bergelora ia menunggang Harimau. Bila bumi lembap dan langit selaras, ia dapat berdiri dan tumbuh sepanjang masa. Syair berikutnya menyebut Kayu Mao berkembang sendiri dengan tenaga yang dalam; pada pertengahan musim semi bukan berarti Logam selalu ditolak, tetapi kemunculan berulang Logam Geng menimbulkan kekhawatiran terhadap Monyet Shen dan Ayam You, sedangkan kemunculan berulang Babi Hai dan Tikus Zi membuat Air Ren dan Gui perlu diwaspadai. Enam benturan membawa tanda daun gugur, tiga keharmonisan membentuk hutan, dan bila pada jam atau hari Logam musim gugur terlalu berat, perjalanan lebih jauh ke barat mendatangkan tekanan yang sulit ditahan. Kayu menjadi susunan pertama dalam batang langit; pada mulanya ia belum memiliki cabang, daun, dan akar. Agar bertahan lama di antara langit dan bumi, ia harus menancapkan diri sangat dalam ke tanah berpasir. Bila dibentuk menjadi balok, Logam memperoleh kegunaan; bila berubah menjadi abu, Api menjadi bencana. Sebagai benda yang kukuh tanpa siasat, ia membiarkan musim semi dan musim gugur datang dan pergi dengan sendirinya.

# === Kesimpulan ===
- kesimpulan_narrative: DN adalah pribadi yang kuat, terbuka, hangat, dan mudah mengambil peran penting di tengah orang lain. Ia mempunyai naluri menolong yang besar, cepat memahami keadaan, dan cenderung menjadi tempat bergantung bagi orang yang lebih muda maupun kelompok yang membutuhkan arah. Kemampuan memimpin ini tumbuh bersama sifat jujur, keberanian, ketegasan, dan dorongan untuk maju. Namun, kekuatan yang sama dapat berubah menjadi sikap terlalu ikut campur, keras kepala, atau terlalu cepat mengambil alih urusan orang lain. Karena itu, perjalanan terbaik bagi DN bukanlah mengurangi kepedulian, melainkan belajar menolong dengan izin, memberi ruang, dan menyampaikan ketegasan secara lebih lembut. Dalam hubungan keluarga dan pasangan, kesungguhan DN sangat kuat. Ia tidak menyukai hubungan yang dimainkan dan menuntut standar yang tinggi dari diri sendiri maupun orang terdekat. Sikap ini dapat membangun kesetiaan, tetapi juga mudah menimbulkan pertengkaran bila kecemburuan, tuntutan, atau perbedaan tidak dibicarakan dengan tenang. Pernikahan yang dipilih setelah pertimbangan matang lebih sesuai daripada keputusan yang terburu-buru. Kecocokan dengan Shio Tikus dan Naga memberi gambaran hubungan yang saling melengkapi, sedangkan hubungan dengan Shio Harimau, Ular, dan Babi memerlukan kewaspadaan lebih besar karena sumber menunjukkan lebih banyak tekanan, kesulitan, dan gangguan kesehatan atau keluarga. Hubungan dengan anak juga membutuhkan kesabaran. Anak dapat keras dalam mengejar keinginan, membutuhkan perhatian besar pada masa kecil, dan baru kemudian berkembang menjadi pendamping yang membantu. Dengan saudara, teman, bawahan, dan rekan kerja, DN perlu menjaga konsistensi komunikasi serta membangun batas kepercayaan yang jelas. Jumlah orang dekat mungkin tidak banyak, tetapi hubungan yang dijaga dengan baik dapat menjadi sumber bantuan nyata. Dalam pekerjaan, DN mempunyai pilihan yang luas. Bidang panas, cahaya, listrik, optik, fotografi, makanan, kecantikan, kosmetik, militer, kesehatan, pelayanan, hukum, perjalanan, perairan, perdagangan, dan pekerjaan lapangan semuanya muncul dalam sumber. Ia juga mempunyai bakat dalam seni, desain, dekorasi, musik, sastra, menulis, teknik, serta pembelajaran mandiri. Posisi yang memberinya tanggung jawab nyata, kesempatan memimpin, dan ruang menggunakan kemampuan praktis akan terasa hidup baginya. Meski demikian, ada masa ketika peran perencana, pendamping utama, atau staf strategis justru membuat kemampuannya lebih leluasa berkembang daripada memegang jabatan tertinggi. Secara finansial, DN mampu membangun hasil melalui kekuatan sendiri dan peluang yang lebih besar terbuka setelah usia pertengahan. Tantangan utamanya bukan sekadar memperoleh uang, melainkan mempertahankan dan mengubahnya menjadi sesuatu yang tahan lama. Karena uang mudah keluar, aset tidak bergerak menjadi sarana penting untuk menjaga nilai. Ia berpotensi memiliki banyak properti, tetapi perlu rencana yang jelas agar aset tersebut tidak hanya tersimpan tanpa dimanfaatkan secara luwes. Kesehatan secara umum memiliki daya pulih yang baik, tetapi DN tetap perlu memperhatikan tenggorokan, gigi, lambung, tulang, persendian, hati, empedu, saraf, sirkulasi kaki, serta risiko luka dari benda tajam, mesin, dan fasilitas logam. Menghindari perkelahian, tempat kerja berbahaya, dan kebiasaan menunda pemeriksaan akan sangat membantu. Periode 2026 sampai 2031 memperlihatkan perubahan yang cukup kuat. Tahun 2026 menonjolkan hasil dari pikiran, tetapi juga menuntut kewaspadaan terhadap konflik, perkara, kesehatan, dan kestabilan rumah tangga. Tahun 2027 membawa peluang sukacita dan tabungan, disertai tekanan kesehatan dan suasana hati. Tahun 2028 merupakan fase perubahan pekerjaan, tempat tinggal, pengeluaran, kesehatan kronis, serta hubungan; keputusan yang gegabah harus dihindari. Tahun 2029 masih membawa perubahan dan pengeluaran, tetapi juga memberi tanda perbaikan bagi keadaan yang sebelumnya kurang baik, kreativitas, dan keberuntungan. Tahun 2030 membutuhkan perhatian terbesar pada tekanan, pengeluaran, kesehatan, keamanan, orang yang berniat buruk, dan kabar dari kerabat atau teman. Tahun 2031 membuka bantuan dari orang tua atau pembimbing, peluang finansial, penghargaan, pembelajaran, dan kemajuan melalui peran strategis. Secara keseluruhan, hidup DN paling berkembang ketika keberanian dipadukan dengan kesabaran, kepedulian dipadukan dengan batas yang sehat, dan pendapatan dipadukan dengan disiplin menjaga aset. Ia tidak kekurangan daya untuk maju. Yang menentukan kualitas hasilnya adalah kemampuan menuntaskan apa yang dimulai, tidak terlalu cepat bereaksi, tidak membiarkan pendapat sekitar mengacaukan keputusan, dan tetap rendah hati ketika kepercayaan serta kewenangan berada di tangannya.

## TAFSIR

### Kepribadian

paragraf:
DN adalah sosok dengan elemen utama Kayu Yang [[甲木]] dalam format Bixing [[比肩格]], yang mencerminkan kepribadian mandiri, berani, dan penuh semangat bersaing. Dengan Api (火) sebagai yong shen [[用神]] dan Air (水) sebagai xi yong shen [[喜神]], ia memerlukan lingkungan yang dinamis dan mendukung ekspresi diri. Sebaliknya, Metal [[金]] sebagai ji shen adalah elemen yang perlu diwaspadai dalam pilihan karir dan relasi.

power:
- Berjiwa pemimpin alami yang selalu menjadi figur inti dan tulang punggung dalam setiap komunitas atau organisasi
- Hangat, ramah, dan mudah bergaul dengan siapa pun — dipercaya sepenuhnya oleh mereka yang lebih muda

shadow:
- Suka turut campur urusan orang lain, sehingga rentan dianggap menyebalkan atau kurang menghargai batasan oleh yang lebih senior
- Sifat keras kepala dan terlalu bersemangat bisa membuat orang lain merasa tertekan atau tidak nyaman

optimum:
- Gunakan naluri kepemimpinan alami untuk memimpin dan menginspirasi tim, bukan sekadar ikut campur secara berlebihan
- Kembangkan kelenturan dan kelembutan dalam berinteraksi untuk membangun koneksi yang harmonis lintas generasi

### Kepribadian Detail

poin:
- DN menjunjung kesetiaan dan tidak segan mengeluarkan harta; ia terus terang tanpa kepura-puraan, tidak mudah melekat, dan dapat memanfaatkan uang yang tersedia dengan murah hati serta sikap yang relatif sederhana. Walaupun mampu mengelola keuangan, ia tidak memandang harta sebagai pusat hidup. Ia ingin mengendalikan benda atau perkara konkret yang memang berada dalam jangkauannya, tetapi tidak terus melekat pada benda atau perkara tersebut.
- DN tidak selalu mengikuti pandangan umum. Ia memiliki keberanian, tidak mudah mengaku kalah, dapat bersikap dominan, keras, dan tajam, serta mempunyai ketegasan dalam mengambil keputusan dan kemampuan memimpin yang kuat.
- Ketika membuat pengelompokan atau analogi, DN cenderung ingin menyertakan banyak contoh. Ia tidak ingin melanggar batas orang lain dan juga tidak ingin batasnya dilanggar. Walaupun tidak selalu membantah pendapat orang lain, ia pun tidak menerimanya begitu saja. Dari luar ia tampak beradab, tetapi kadang kurang luwes dalam pergaulan dan tidak terlalu suka banyak bicara.
- DN menaruh perhatian pada dunia material yang konkret, tetapi tidak melekat pada benda. Ia cakap menangani hal praktis, memiliki daya tangkap yang kuat, dorongan untuk maju, watak teguh dan berprinsip, serta hati yang baik dan lurus. Namun, kemampuan beradaptasi secara cepat ketika keadaan berubah perlu dilatih.

### Sekilas Hidup

card:
- Relasi pasangan | Pasangan DN dapat bersikap mengatur dan sesekali sulit diajak bernalar.
- Anak | Putra DN cenderung tidak terlalu menonjolkan keterikatan emosional, cukup murah hati dalam menggunakan uang, dan memiliki kemampuan dalam bidang menulis.
- Hubungan dengan ibu | DN cenderung sulit menerima perkataan ibunya dan komunikasi di antara keduanya relatif tidak banyak.
- Cara berpikir | DN relatif kurang menonjol dalam pemikiran yang panjang atau rumit.
- Wewenang | DN memiliki kecenderungan memegang kuasa atau kewenangan yang cukup besar.
- Kesehatan dan keselamatan | DN perlu mewaspadai gangguan tulang, persendian, hati dan empedu, kejang, serta kelemahan saraf. Ia juga lebih mudah mengalami luka akibat pisau, senjata, benda logam, atau benturan dan tekanan, sehingga sebaiknya menghindari perkelahian serta tidak mendekati motor, ruang mesin, atau fasilitas logam berbahaya.
- Pertemuan pasangan | Peluang DN berkenalan dengan pasangan berkaitan dengan pekerjaan atau urusan karier.

### Keluarga & Pasangan

pasangan:
- vibe: Dinamis & Perlu Keseimbangan
- headline: Pasangan ideal dari Shio Tikus atau Naga
- cocok_list:
  - shio: 鼠
    label: 大吉
    teks: Bak permata yang saling melengkapi, perjalanan bersama akan mulus dan lancar. Kesuksesan, kemakmuran, dan keturunan yang berkembang hadir bersama.
  - shio: 龍
    label: 大吉
    teks: Bak permata yang saling melengkapi, perjalanan bersama akan mulus dan lancar. Tidak ada halangan yang berarti — kemakmuran keluarga berlanjut lima generasi.
- hindari_list:
  - shio: 虎
    teks: Pada awal bersama, bencana datang silih berganti. Di pertengahan hidup mungkin terjadi musibah besar, kehilangan sandaran orang tua saat muda, atau umur yang tidak panjang — penyakit dan kesulitan menghampiri.
  - shio: 蛇
    teks: Pada awal bersama, bencana datang silih berganti. Malapetaka dan penyakit yang menyengsarakan dapat menghampiri sepanjang perjalanan hidup bersama.
  - shio: 豬
    teks: Pada awal bersama, bencana datang silih berganti. Menjelang tua barulah kebahagiaan mungkin hadir — namun jalan menuju kesana penuh dengan rintangan dan kesedihan.

### Karir & Industri

intro: DN memiliki Day Master Kayu Yang dalam format rekan sejajar, dengan Api dan Air sebagai unsur pendukung. Bidang yang berkaitan dengan panas, cahaya, listrik, seni, layanan, kesehatan, perjalanan, perairan, serta perdagangan terbuka baginya, sedangkan lingkungan Logam yang terlalu keras perlu dikelola dengan hati-hati.

### Palace Detail 1

ming_gong:
- star: 紫微、七殺
- insight: DN adalah sosok yang meski memiliki kelemahan sifat lamban dan suka bertele-tele [[拖泥帶水]], namun perjalanan hidupnya tetap cerah dan kokoh. Postur tubuhnya relatif tinggi [[身材較高]], lebih kekar dan sehat dibandingkan orang kebanyakan. Ciri khas utamanya adalah sikap yang hangat dan mudah bergaul dengan siapa pun [[和藹可親]], disertai kemampuan berpikir yang sangat cepat dan tajam. Karakternya lembut dan bersahabat [[性格溫馴待人和氣]], kaya akan keluwesan dan fleksibilitas [[柔軟性]] — namun di sisi lain, ia juga memiliki sisi keras kepala [[執拗]] dan gemar turut campur urusan orang lain. Apapun urusan orang lain, selama ia bersinggungan dengannya, ia pasti akan ikut terlibat. Justru karena naluri bawaan yang gemar membantu ini, bahkan tanpa diminta sekalipun, ia dengan antusias akan mengulurkan tangan [[熱心地幫助]] — sehingga ia memiliki banyak teman, dan dihormati oleh mereka yang lebih muda sebagai kakak tertua yang bisa diandalkan [[足可信賴的老大哥]]. Namun, mereka yang lebih tua cenderung memandangnya sebagai orang yang suka ikut campur urusan orang lain. Bagi perempuan dengan bintang istana kehidupan ini, umumnya termasuk dalam kelompok perempuan berbakat [[才女之流]] yang kemampuannya tak kalah dari kaum pria, bahkan bisa melampaui mereka. Dalam hal apapun, selalu ingin bersaing dan membuktikan diri. Setelah menikah, akan menjadi istri yang cakap sekaligus pemimpin yang tegas [[能幹妻子]], bahkan mampu mengambil alih peran kepemimpinan dari suami. Yang perlu diperhatikan adalah jangan terlalu berlebihan dalam mencampuri urusan pasangan. DN memiliki karakter yang lurus, jujur, dan berjiwa besar [[豪爽正直]], mampu berdiri di atas orang lain dan menempati posisi kepemimpinan [[領導地位]]. Dengan sifat yang terbuka dan teratur dalam bertindak [[爽朗行事也有節制]], ia mudah mendapat kepercayaan dari banyak pihak. Dalam setiap kegiatan kelompok, ia pasti akan menempati posisi pemimpin dan menjadi figur inti [[核心人物]] yang diandalkan oleh komunitas. Apabila bintang Tianji [[天機星]] berada dalam satu istana yang sama, bakat sastra dan kecerdasan intelektual [[文才]] dapat mengantarkannya pada ketenaran, sekaligus mendatangkan keberuntungan finansial. Bagi kaum perempuan dengan konfigurasi ini, sifat yang terlalu maskulin akibat kepribadian yang terlalu bersemangat justru membuat kesan pertama kurang mendalam. Sejak kecil sering bermain bersama anak laki-laki, sehingga kepribadiannya cenderung sedikit ceroboh [[輕佻]] dan tidak terlalu feminin. Namun demikian, mereka yang benar-benar mengenal kejujuran dan ketulusan hatimu [[腸子不虛偽]] pasti akan menaruh kepercayaan yang mendalam padamu. Yang perlu kamu perhatikan hanyalah menjadi sedikit lebih lembut dalam bersikap — dan itu sudah lebih dari cukup.
- action: DN perlu menyalurkan naluri memimpin dan menolong dengan batas yang sehat, meminta persetujuan sebelum ikut campur, serta menyampaikan ketegasan dengan cara yang lebih lembut.

xiongdi:
- star: 天機、天梁
- insight: Istana saudara memberi isyarat adanya perubahan yang mudah terjadi. Perasaan DN dapat berulang kali berubah, sehingga hubungan dengan teman maupun saudara tidak selalu mampu bertahan lama. Walaupun jumlah saudara dan teman dekatnya tidak tergolong banyak, mereka tetap dapat saling membantu ketika diperlukan. Bila konfigurasi ini berada bersama bintang yang kurang menguntungkan, hal kecil yang tidak terduga dapat menyebabkan DN kehilangan hubungan dengan saudara atau teman.
- action: DN perlu menjaga hubungan inti melalui komunikasi yang konsisten dan tidak membiarkan persoalan kecil berkembang menjadi putusnya hubungan.

fuqi:
- star: 太陽、巨門
- insight: DN memiliki pandangan cinta yang sungguh-sungguh dan tidak berniat mempermainkan hubungan. Karena itu, ia sama sekali tidak dapat menerima pasangan yang bersikap ringan atau bermain-main. Standar yang ia terapkan kepada diri sendiri dan pasangannya sama-sama ketat, sehingga perjalanan cintanya mungkin mengalami gelombang yang besar. Karena pengaruh bintang Matahari Tai Yang [[太陽]] terlalu kuat, pernikahan pada usia terlalu muda dinilai kurang menguntungkan. Bila memungkinkan, DN tidak perlu terburu-buru menikah; keputusan sebaiknya dijalankan perlahan setelah pertimbangan yang matang. Bagi pria, konfigurasi ini memberi peluang memperoleh istri yang ceria dan sehat, sedangkan bagi wanita memberi peluang menikah dengan pria yang murah hati dan berjiwa besar. Namun, ketika bintang kurang baik ikut menghalangi, hubungan dapat berhadapan langsung dengan krisis perceraian. Pertengkaran antarpasangan mudah muncul. Meskipun demikian, bila bintang Matahari Tai Yang [[太陽]] berada bersama tanpa bintang buruk lain, atau berada bersama bintang Keharmonisan Langit Tian Tong [[天同]] dan bintang Mekanisme Langit Tian Ji [[天機]], DN dapat memperoleh pasangan yang cerdas dan membangun keluarga yang harmonis. Rasa cemburunya secara alami kuat, tetapi biasanya tidak ia tunjukkan lewat kata-kata. Bagi pria, bila bintang Sastra Wen Chang [[文昌]] dan bintang Mekanisme Langit Tian Ji [[天機]] menempati posisi terkait, ada kecenderungan membangun hubungan atau tempat tinggal lain di luar pernikahan. Pria dengan konfigurasi ini menyukai wanita yang berpenampilan dingin tetapi menarik. Bagi wanita, ada hubungan kuat dengan pria yang berpikiran cerdas dan memiliki daya finansial. Baik pria maupun wanita sama-sama peka terhadap cinta, sehingga tampak mempunyai kecenderungan menikah lebih awal. Pria mungkin menikah dengan wanita yang penuh kebijaksanaan, sedangkan wanita mungkin bertemu pria yang kecerdasannya menonjol; wanita juga cenderung menikah dengan pria bertubuh tinggi. Bila bintang baik lain ikut berada di istana ini, kedekatan emosional suami istri dapat sangat baik. Sebaliknya, bila bintang buruk hadir, sikap ringan dalam hubungan dapat menjadi penyebab perpisahan.
- action: DN perlu memilih pasangan dengan matang, menunda keputusan yang terlalu cepat, menjaga batas kesetiaan, dan membahas kecemburuan serta perbedaan secara terbuka sebelum berubah menjadi pertengkaran.

zinu:
- star: 武曲、貪狼
- insight: DN berpotensi mempunyai putra yang lembut dan patuh, tetapi gerak atau responsnya agak lambat. Ada kemungkinan jumlah keturunan sedikit; sekalipun mempunyai anak, jumlahnya mungkin hanya satu. Bila bintang Tujuh Pembunuh Qi Sha [[七殺]] dan bintang Gerbang Raksasa Ju Men [[巨門]] ikut berada di istana anak, terdapat risiko mengalami perpisahan berat dengan anak. Bila bersama bintang Serigala Rakus Tan Lang [[貪狼]], pada masa tua DN dapat menerima berkah dan dukungan dari anak. Bila bintang Bela Diri Wu Qu [[武曲]] berada sendiri tanpa bintang lain, anak yang lahir dari hubungan di luar pasangan atau anak angkat justru lebih mungkin membantu keberhasilan DN. Walaupun memiliki keturunan, anak dapat sering menghindar, menentang, atau tidak mampu memberikan bantuan yang diharapkan. Jika bintang Bela Diri Wu Qu [[武曲]] kembali hadir bersama, anak memerlukan perhatian dan perawatan besar pada masa kecil, tetapi setelah dewasa dapat menjadi tangan kanan yang membantu perkembangan DN. Bila hanya bintang Serigala Rakus Tan Lang [[貪狼]] yang menempati posisi ini, anak DN tidak mudah berhenti sebelum memperoleh hal yang diinginkannya.
- action: DN perlu mengasuh dengan sabar sejak dini, memberi batas yang jelas tanpa memutus kedekatan, dan mengarahkan kegigihan anak menjadi kemampuan produktif.

### Palace Detail 2

caibo:
- star: 天同、太陰
- insight: Sumber kekayaan tidak tetap atau spekulatif DN tidak tergolong berlimpah. Ketika mempunyai uang, ia cenderung sulit mempertahankannya; pembelian aset tidak bergerak menjadi cara yang lebih baik untuk menjaga nilai kekayaan. Walaupun kaitannya dengan rezeki tidak tetap cukup kuat, jenis rezeki ini tidak mudah diperoleh. Sumber pendapatan tetap DN juga tidak tergolong berlimpah. Uang yang tersedia relatif sulit disimpan, sehingga aset tidak bergerak kembali menjadi sarana penting untuk mempertahankannya. Hubungannya dengan penghasilan tetap cukup kuat, tetapi penghasilan itu tetap memerlukan usaha dan tidak datang dengan mudah. Dalam istilah sumber, rezeki tetap Zheng Cai [[正財]] berarti sumber penghasilan yang bersifat tetap, seperti gaji, sedangkan rezeki sampingan Pian Cai [[偏財]] berarti sumber yang bersifat peluang, seperti komisi. DN sangat murah hati ketika membelanjakan uang, tetapi pada saat yang sama mampu memperoleh kembali imbalan yang sepadan. Ia berpotensi membangun usaha dari nol dengan kekuatan pribadi dan memegang sendiri kesempatan menghasilkan uang, sedangkan fase menghasilkan kekayaan besar cenderung dimulai setelah usia pertengahan. Bila berada bersama bintang Balok Langit Tian Liang [[天梁]], ia dapat menjadi pengusaha nyata yang cukup berpengaruh. Sekalipun ada bintang kurang baik, pilihan profesi sebagai dokter, akademisi, seniman, atau ahli peramalan tetap dapat memberikan keberuntungan finansial yang cukup baik. Bintang Bulan Tai Yin [[太陰]] memiliki ikatan dengan harta. Bila bersama bintang Mekanisme Langit Tian Ji [[天機]], DN dapat berangkat tanpa modal berarti lalu menghasilkan kekayaan yang cukup besar. Bila bersama bintang Keharmonisan Langit Tian Tong [[天同]], ia kerap menjumpai kesempatan memperoleh uang besar. Bila bersama bintang baik lainnya, uang yang masuk dapat disimpan dan berkembang sehingga ia menjadi pemilik aset yang cukup kuat. Pada dasarnya DN tidak perlu terlalu khawatir akan dikekang oleh masalah uang. Namun, bila konfigurasi berada di cabang Macan Yin [[寅]] atau Kuda Wu [[午]], daya bintang Sastra Wen Chang [[文昌]] melemah; akibatnya kekayaan sulit ditumpuk dan uang dapat habis dalam waktu singkat.
- action: DN sebaiknya mengubah kelebihan arus kas menjadi aset nyata dan memakai aturan simpan otomatis agar pendapatan tetap maupun peluang tidak cepat habis.

jie_e:
- star: 天府
- insight: DN cenderung mudah mengalami gangguan tenggorokan, flu, sakit gigi, dan keluhan sejenis. Secara umum ia jarang terserang penyakit atau cedera; bila sakit, pemulihan melalui pengobatan juga cenderung berlangsung cepat. Bila berada bersama bintang yang kurang baik, ia lebih mudah mengalami gangguan lambung, beri-beri, atau keluhan sejenis. Bila berada bersama bintang Kaisar Ungu Zi Wei [[紫微]], kondisi kesehatannya sangat baik dan tidak perlu terlalu mencemaskan penyakit.
- action: DN sebaiknya menjaga tenggorokan, kesehatan gigi, pola makan, dan sirkulasi kaki, serta segera memeriksakan keluhan agar kecenderungan pulih cepat dapat dimanfaatkan.

qianyi:
- star: null
- insight: Dalam pergerakan, perjalanan, dan perubahan lingkungan, DN mempunyai rasa stabil. Ia tidak cenderung menerobos secara membabi buta dan relatif kecil kemungkinannya tersesat ke arah atau jalan yang keliru. Sikap bergeraknya lebih terukur daripada impulsif.
- action: DN dapat mempertahankan kebiasaan memeriksa arah dan tujuan sebelum mengambil langkah besar di luar lingkungan yang sudah dikenal.

puyi:
- star: 廉貞、破軍
- insight: DN cenderung memiliki bawahan yang sangat bergantung dan menuntut perhatian rinci darinya. Ia mungkin sering merasa dirugikan oleh bawahan yang melawan. Bila istana berada pada cabang Babi Hai [[亥]], bawahan dapat mengkhianati kepercayaannya, tetapi pada masa tua DN dapat memperoleh dukungan dari bawahan yang kuat. Bila bersama bintang Serigala Rakus Tan Lang [[貪狼]], DN berisiko hanya dijadikan alat oleh bawahan. Bila bersama bintang Tujuh Pembunuh Qi Sha [[七殺]], ia sering menghadapi pengkhianatan teman. Bila bersama bintang Keharmonisan Langit Tian Tong [[天同]], jumlah teman muda dan bawahannya banyak. Bila istana berada pada cabang Tikus Zi [[子]], Naga Chen [[辰]], Kuda Wu [[午]], Anjing Xu [[戌]], atau Babi Hai [[亥]], bawahannya termasuk orang yang memiliki kemampuan nyata. Walaupun masih muda, cukup banyak temannya yang berbakat. Bila bersama bintang Kaisar Ungu Zi Wei [[紫微]], bawahan atau teman yang lebih muda sering membantu DN secara diam-diam. Pada konfigurasi istana lain, bawahan dapat menyimpan kebencian lalu mengkhianatinya, sementara teman yang lebih muda justru mungkin membalas keburukan dengan kebaikan.
- action: DN perlu membangun sistem kerja, batas kewenangan, dan pemeriksaan kepercayaan yang jelas agar bantuan bawahan tidak berubah menjadi ketergantungan atau pengkhianatan.

### Palace Detail 3

guanlu:
- star: null
- insight: Sumber istana karier menyebutkan bahwa DN sesuai menjalani pekerjaan sebagai dokter, perawat, pengasuh anak, pengacara, dan pekerjaan lain yang sejenis. Arah ini menempatkan pelayanan, perawatan, perlindungan, dan pendampingan profesional sebagai jalur kerja yang relevan bagi DN.
- action: DN dapat memprioritaskan profesi yang memadukan tanggung jawab, pelayanan langsung, dan keahlian profesional.

tianzhai:
- star: null
- insight: DN berpotensi memiliki aset tidak bergerak dalam jumlah besar. Namun, ia cenderung kurang luwes dalam memanfaatkan, mengelola, atau mengembangkan penggunaan aset-aset tersebut, sehingga besarnya kepemilikan belum tentu langsung menghasilkan manfaat yang optimal.
- action: DN perlu membuat rencana fungsi, hasil, dan waktu evaluasi untuk setiap properti agar aset besar tidak berhenti sebagai kepemilikan pasif.

fude:
- star: null
- insight: DN memiliki pembawaan yang cerah, menarik, dan lembut; baik pria maupun wanita dengan konfigurasi ini umumnya mempunyai hubungan sosial yang baik. Istana ini memberi isyarat bahwa ia dapat menerima berkah kebahagiaan. Ia cukup cakap menghadapi kehidupan dan sangat memperhatikan cara berhubungan dengan orang lain. Namun, bila pendapat di sekelilingnya mengacaukan keputusan, keberuntungan yang sudah berada di tangan dapat menghilang. Berkah cenderung menyertai DN sepanjang hidup dan sekaligus mendukung umur panjang. Ia juga mempunyai kecenderungan mengejar impian yang romantis. Bila hanya bintang Bulan Tai Yin [[太陰]] berada di istana kebahagiaan, ia sudah dapat menjalani hidup yang sangat beruntung. Bila bintang Matahari Tai Yang [[太陽]] turut hadir, ia hampir pasti berpeluang menikmati kehidupan bahagia yang memuaskan tubuh dan batin. Namun, bila bersama bintang Mekanisme Langit Tian Ji [[天機]], pikirannya hampir tidak pernah benar-benar beristirahat. Konfigurasi ini memberi tanda kuat tentang kebahagiaan dan umur panjang. DN juga mempunyai sisi tenang dan tidak terlalu memusingkan keadaan; bahkan ketika menghadapi krisis besar, ia dapat tetap tidak panik dan menanganinya dengan tenang. Akan tetapi, bila istana berada pada cabang Macan Yin [[寅]] atau Kelinci Mao [[卯]], atau bila bintang kurang baik menghalangi, ketenangan sulit diperoleh dan hidup menjadi penuh perubahan. Bila kekerasan batin berkembang menjadi kesombongan, DN dapat memilih kehidupan yang sunyi dan berdiri sendiri.
- action: DN perlu menjaga ketenangan batin, menyaring pendapat luar, memberi ruang istirahat bagi pikiran, dan memastikan keteguhan tidak berubah menjadi kesombongan atau keterasingan.

fumu:
- star: 七殺
- insight: Orang tua DN dapat tampak murung dan kurang menunjukkan semangat. Di sisi lain, ia memiliki orang tua yang unggul dan berkedudukan sosial cukup tinggi. Hubungan orang tua dan anak pada dasarnya dapat berlangsung harmonis. Kedua orang tua juga rajin menabung dan mungkin meninggalkan harta yang besar bagi DN. Karena pengaruh mereka, kebiasaan menabung yang kuat kemungkinan telah tertanam dalam dirinya sejak awal. Orang tuanya sangat memperhatikan tata krama dan berusaha sungguh-sungguh mendidik keluarga. Bila hubungan dengan orang tua tidak harmonis, penyebabnya kemungkinan karena mereka menyimpan keraguan terhadap tindakan DN. DN juga dapat berpisah dari orang tua atau anggota keluarga sejak relatif dini. Orang tuanya merupakan pribadi keras dan tidak mudah berkompromi; bila DN tidak bertindak sesuai kehendak mereka, ia sulit memperoleh pengertian. Namun, mereka juga tidak mudah menolak permintaan orang lain. Sikap yang bertentangan ini dapat menimbulkan konflik mendalam antara DN dan orang tua. Bila berada bersama bintang Kaisar Ungu Zi Wei [[紫微]] atau beberapa bintang baik, risiko perpisahan atau putusnya hubungan orang tua dan anak berkurang. Walaupun demikian, pengaruh bintang Tujuh Pembunuh Qi Sha [[七殺]] tetap perlu diingat sebagai unsur yang membawa tekanan.
- action: DN perlu menjaga hormat tanpa kehilangan batas pribadi, membicarakan keputusan penting lebih awal, dan memisahkan perbedaan cara berpikir dari kasih keluarga.

### Sintesis & Saran Aksi

opening: DN adalah sosok berjiwa pemimpin yang hangat, jujur, dan penuh semangat membantu — dengan kemampuan berpikir cepat dan naluri sosial yang kuat, ia mampu menjadi figur inti yang diandalkan dalam komunitas maupun organisasi.

trio:
  kekuatan: Kepemimpinan alami yang kuat, mudah mendapat kepercayaan luas, dan mampu menginspirasi orang-orang di sekitarnya untuk berkembang.
  tantangan: Sifat terlalu ikut campur dan keras kepala bisa menciptakan gesekan dengan pihak yang lebih senior atau mereka yang menghargai ruang pribadinya.
  tindakan: Pelajari seni kepemimpinan yang memberdayakan — pimpin dengan memberi ruang, bukan dengan mengambil alih setiap situasi.

actions:
- title: Perkuat Peran Pemimpin
  context: Naluri kepemimpinan alami DN adalah aset terbesar — arahkan ke posisi yang memberikan tanggung jawab nyata dan dampak luas.
  tag: Karir
- title: Kelola Batasan Relasi
  context: Sifat gemar membantu perlu diimbangi dengan kepekaan terhadap privasi orang lain agar tidak dianggap terlalu ikut campur.
  tag: Relasi
- title: Aktifkan Unsur Api
  context: Yong shen Api (火) berarti ekspresi dan produktivitas adalah kunci — jadikan kreativitas dan aksi nyata sebagai prioritas harian.
  tag: Energi
- title: Bangun Jaringan Lintas Generasi
  context: Saat sudah dipercaya oleh yang lebih muda, saatnya membangun hubungan yang lebih harmonis dengan yang lebih senior melalui pendekatan yang lebih lembut.
  tag: Networking
- title: Hindari Lingkungan Metal Berlebih
  context: Ji shen Metal (金) perlu diwaspadai — hindari lingkungan atau partner yang terlalu rigid, kaku, atau destruktif terhadap pertumbuhan.
  tag: Proteksi
