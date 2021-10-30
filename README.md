# オンラインのアイスブレイクツールMeltice

[![IMAGE ALT TEXT HERE](https://jphacks.com/wp-content/uploads/2021/07/JPHACKS2021_ogp.jpg)](https://www.youtube.com/watch?v=LUPQFB4QyVo)

![IMAGE ALT TEXT](https://raw.githubusercontent.com/jphacks/F_2105/master/system/static/images/meltice-logo-dark.png)

## 製品概要
### 背景(製品開発のきっかけ、課題等）
コロナにより、テレワークが急速に進み、それに応じてウェブ会議が急速に普及しました。一方で、ウェブ会議をする今、「円滑なコミュニケーションができない」「相手に共感しにくい」などの問題が発生しております。これらの問題をウェブ会議開始数分前にアイスブレイクをすることで解決することができるのではないかと考えました。そのためのツールを開発しました。
### 製品説明（具体的な製品の説明）

#### 対象とする利用者
- 人事の方(以下、人事、とします)
- アイスブレイク参加者の方(以下、参加者、とします)

#### 発表資料
![im 1](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/1.png)
![im 2](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/2.png)
![im 3](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/3.png)
![im 4](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/4.png)
![im 5](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/5.png)
![im 6](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/6.png)
![im 7](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/7.png)
![im 8](https://raw.githubusercontent.com/jphacks/F_2105/master/expression-images/8.png)

### 特長
このシステムは、ウェブ会議で事前にアンケートをした結果を基に話題提供し、評価を提供します。これは世界初のシステムです。
#### 1. 特長1
参加者の興味を事前にアンケートの形式で取得できます。
#### 2. 特長2
参加者のオンラインでの盛り上がり度を可視化できます。
#### 3. 特長3
面倒なインストールをする必要がなく、契約当日から利用することができます。

### 解決出来ること
ウェブ会議で参加者が本当に集中しているのかということを可視化できます。また、話題を作るのに、ビジネスニュースに観点を当てることで、労働者のビジネスへの関心を高めることができます。

### 今後の展望
将来的には、日本に限らず、世界に向けて展開することや、ビジネスニュースだけでなく宴会でのゲームなどのカジュアルにも展開することを考えております。

### 注力したこと（こだわり等）
- APIにすることで、開発速度を上げました。
- Vueを用いることで、開発速度を上げました。
- Issuesに開発過程を書くことで、メンバーの状況を可視化しました。

## 開発技術
### 活用した技術
#### API・データ
- [Firebase Realtime Database](https://firebase.google.com/docs/database)にデータを保存することで、読込書込のしやすいシステムを実現しました。
- 

#### フレームワーク・ライブラリ・モジュール
- 機械学習ライブラリーとして[PyTorch](https://pytorch.org/)を用いました。
- JavaScriptのフレームワーク[Vue](https://vuejs.org/)を用いました。
- Vueのボタン部分のために[Vuetify](https://vuetifyjs.com/)を用いました。
- サーバーとしてFlaskを用いました。

#### デバイス
- ブラウザー（EdgeやChromeなどのアプリ）とウェブ会議ができるシステム（ZoomやGoogle Meet）があれば、どなたでも利用できます。

### 独自技術
#### ハッカソンで開発した独自機能・技術
- 独自で開発したものの内容をこちらに記載してください
- 利用はしやすい一方で、5年前からPyPIでの開発がストップしていたPyrebaseというサードパーティーライブラリーを[独自に書き換えた](https://github.com/jphacks/F_2105/tree/master/system/pyrebase21)。

#### 製品に取り入れた研究内容（データ・ソフトウェアなど）（※アカデミック部門の場合のみ提出必須）
- 表情認識にはIEEE ICPR 2020で採択された[Residual Masking Network](https://ieeexplore.ieee.org/document/9411919)を用いた。

## システム開発者紹介
TEAM TOKIのメンバー
- [Nozomi Toba](https://withcation.com)
- [Tatsuya Ichino](https://github.com/roaris)
- [Yu Osaka](https://github.com/yud0uhu)
- [Yoshiyuki Kubota](https://yocchi0425.github.io/self-introduction/) 

## For Developers

### git clone
- `git clone https://github.com/jphacks/F_2105`
- `cd F_2105`

### environment
- NEED .env file (please ask me: [278Mt](https://github.com/278Mt))

#### operability confirmed
- Python 3.9
- macOS 11.5.2
- Chrome 94.0.4606.81

### pip install
- `pip install -r requirements.txt`

### run server
- `python app.py`
  - you cannot use the command: `flask run`.

