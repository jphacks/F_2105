// 現在のURLを取り出してきてlocalhostならデバッグモードにする
const isDebug = location.host == '127.0.0.1:5000'; // eslint-disable-line no-unused-vars
const melticeDarkBlue = 'rgb( 12,  75, 126)'; // eslint-disable-line no-unused-vars
// const melticeBlue = 'rgb( 90, 155, 211)'; // eslint-disable-line no-unused-vars
const melticeBlue = 'rgb( 12,  75, 126)'; // eslint-disable-line no-unused-vars
const melticeLightBlue = 'rgb(213, 230, 244)'; // eslint-disable-line no-unused-vars

// 逆オウム返し
// eslint-disable-next-line no-unused-vars
var vmTorrap = new Vue({
  el: '#torrap',
  data: {
    text: '僕は37歳で、そのときボーイング747のシートに座っていた。',
    res: 'pretext',
  },
  methods: {
    torrapCommunicate: function () {
      axios
        .post('/api/communicate-torrap', { text: this.text })
        .then((response) => {
          this.res = response.data.res;
          console.log(`res: ${this.res}`);
        });
    },
  },
});

// eslint-disable-next-line no-unused-vars
var vmHeader = new Vue({
  el: '#header',
  methods: {
    navPoint(link) {
      if (location.pathname === link) {
        return { current: true };
      } else {
        return { current: false };
      }
    },
  },
});

// アーキテクチャー的にコンポーネントにした方が楽な場合がある
// https://forum.vuejs.org/t/change-div-background-color-on-click/75549#:~:text=architectural
Vue.component('wanted-news-list', {
  template: `
    <div
      class="wanted-news-list"
      @click="newsSelect"
      :style="{
        'background-color': is_wanted ? melticeBlue : melticeLightBlue
        }">
      <p
        :style="{
          'color': is_wanted ? 'white' : 'black'
        }">{{ news.title }}</p>
      <img :src="news.imgsrc">
      <a
        :href="news.url"
        target="blank"
        :style="{
          'color': is_wanted ? 'white' : 'blue'
        }">
        詳しく見る
      </a>
    </div>
  `,
  props: {
    news: Object,
  },
  data: function () {
    return {
      is_wanted: false,
    };
  },
  methods: {
    newsSelect: function () {
      this.is_wanted = !this.is_wanted;
      console.log(`is_wanted: ${this.is_wanted}`);
      this.$emit('is_wanted', this.is_wanted);
    },
  },
});

// eslint-disable-next-line no-unused-vars
var vmNews = new Vue({
  el: '#news',
  data: {
    news_list: [],
    range_end: 6,
    range_shift: 6,
    zoom_id: '',
    isAlert: false
  },
  computed: {
    newsSuggest: function () {
      axios.get('/api/suggest-news').then((response) => {
        this.news_list = response.data.res;
        console.log(this.news_list);
      });
    },
  },
  methods: {
    moreNewsSuggest: function () {
      this.range_end += this.range_shift;
    },
    // 選んだニュースを送信し保存
    newsSave: function () {
      if (this.zoom_id === '') {
        window.alert('zoom idを入力してください');
        return;
      }
      for (let i = 0; i < this.news_list.length; ++i) {
        const news = this.news_list[i];
        console.log(news.is_wanted);
        if (news.is_wanted) {
          axios
            .post('/api/save-news', {
              url: news.url,
              news_id: news.news_id,
              title: news.title,
              imgsrc: news.imgsrc,
              zoom_id: this.zoom_id,
            })
            .then((response) => {
              this.result = response.data.status;
              console.log(`status: ${this.result}`);
            });
          this.isAlert = true;
        }
      }
      if (this.isAlert) {
        window.alert('送信しました！');
      }
    },
  },
});

// eslint-disable-next-line no-unused-vars
var vmEnquete = new Vue({
  el: '#enquete',
  data: {
    news_list: [],
    name: '',
    isAlert: false,
  },
  computed: {
    // 人事によって選ばれた近日のニュースを提示
    newsQuestion: function () {
      axios.get('/api/question-news').then((response) => {
        this.news_list = response.data.res;
        console.log(this.news_list);
        for (let i = 0; i < this.news_list.length; ++i) {
          this.news_list[i].is_wanted = false;
        }
      });
    },
  },
  methods: {
    // 興味があるニュースを登録
    degreeSave: function () {
      if (this.name.length === 0) {
        window.alert('名前を入力してください');
        return;
      }
      for (let i = 0; i < this.news_list.length; ++i) {
        const news = this.news_list[i];
        axios
          .post('/api/save-degree', {
            name: this.name,
            news_id: news.news_id,
            degree: news.is_wanted ? 10 : 1,
          })
          .then((response) => {
            `status: ${console.log(response.data.status)}`;
          });
        this.isAlert = true;
      }
      if (this.isAlert) {
        window.alert('送信しました！');
      } else {
        window.alert('ニュースを選択してください');
      }
    },
  },
});

// ルームの参加者を登録
// eslint-disable-next-line no-unused-vars
var vmRoom = new Vue({
  el: '#room',
  data: {
    name: '',
    zoom_id: '',
  },
  methods: {
    roomSet: function () {
      if (this.name.length === 0) {
        window.alert('名前を入力してください');
        return;
      }
      if (this.zoom_id.length === 0) {
        window.alert('zoom idを入力してください');
        return;
      }
      axios
        .post('/api/set-room', {
          name: this.name,
          zoom_id: this.zoom_id,
        })
        .then((response) => {
          console.log(response.data.res);
          this.speechSave();
        });
    },
    speechSave: function () {
      // 参考資料: https://github.com/tokjin/autoSpeechRecognition
      const SpeechRecognition = webkitSpeechRecognition || SpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = 'ja-JP';
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onresult = (event) => {
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          let transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalText += transcript;
          }
        }
        if (finalText.length > 0) {
          console.log(`text: ${finalText}`);
          axios
            .post('/api/save-speech', {
              name: this.name,
              zoom_id: this.zoom_id,
              text: finalText,
            })
            .then((response) => {
              console.log(`responded text: ${response.data.res.text}`);
            });
        }
      };

      recognition.onerror = (e) => {
        console.log('onerror', e);
        if (e.error == 'no-speech') {
          try {
            recognition.stop();
          } catch (e) {
            console.error(e);
          }
          setTimeout(() => {
            try {
              recognition.start();
            } catch (e) {
              console.error(e);
            }
          }, 500);
        } else {
          try {
            recognition.stop();
          } catch (e) {
            console.error(e);
          }
          setTimeout(() => {
            try {
              recognition.start();
            } catch (e) {
              console.error(e);
            }
          }, 500);
        }
      };

      recognition.onspeechend = () => {
        setTimeout(() => {
          try {
            recognition.start();
          } catch (e) {
            console.error(e);
          }
        }, 500);
      };

      recognition.start();

      setTimeout(() => {
        try {
          recognition.start();
        } catch (e) {
          console.error(e);
        }
      }, 2000);
    },
  },
});

// eslint-disable-next-line no-unused-vars
var vmSuggestion = new Vue({
  el: '#suggestion',
  data: {
    zoom_id: '',
    news: {},
  },
  methods: {
    // 登録参加者の興味に応じて初期のニュースを送信
    newsSet: function () {
      if (this.zoom_id.lendth === 0) {
        window.alert('名前を入力してください');
      }
      axios
        .post('/api/set-news', {
          zoom_id: this.zoom_id,
        })
        .then((response) => {
          this.news = response.data.res;
          console.log(this.news);
        });
      setInterval(this.topicChange, 5000);
    },
    // 興味に応じてニュースを変える
    topicChange: function () {
      axios
        .post('/api/change-topic', {
          zoom_id: this.zoom_id,
          news_id: this.news.news_id,
          title: this.news.title,
        })
        .then((response) => {
          console.log(`res: ${response.data.status}`);
          if (response.data.status === 'CHANGE') {
            this.news = response.data.res;
          }
        });
    },
  },
});

// 参加者の名前を表示
// eslint-disable-next-line no-unused-vars
var vmComputing = new Vue({
  el: '#computing',
  data: {
    names: [],
    post_names: new Array(5),
    sounds: {},
    zoom_id: '',
    movie: null,
    errorMessage: null,
  },
  methods: {
    namesSet: function () {
      axios
        .post('/api/set-names', {
          zoom_id: this.zoom_id,
        })
        .then((response) => {
          this.names = response.data.res;
          console.log(this.names);
          this.errorMessage = null; // エラーメッセージのリセット
        })
        .catch(() => {
          // zoom idが存在しない場合
          this.names = []; // 表示をリセット
          this.errorMessage = '指定のzoom idは存在しません';
        });
    },
    movieSet: function (event) {
      event.preventDefault();
      this.movie = event.target.files[0];
    },
    soundSet: function (event, name) {
      event.preventDefault();
      this.sounds[name] = event.target.files[0];
    },
    movieSoundUpload: function () {
      let formData = new FormData();
      formData.append('movie', this.movie);
      for (let i = 0; i < this.names.length; ++i) {
        let name = this.names[i];
        formData.append(`sound-${name}`, this.sounds[name]);
      }
      formData.append('zoom_id', this.zoom_id);
      formData.append('names', this.post_names);

      axios
        .post('/api/save-evaluation', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then((response) => {
          console.log(`res: ${response.status}`);
        });
    },
  },
});

// 評価を表示
// eslint-disable-next-line no-unused-vars
var vmEvaluationSave = new Vue({
  el: '#analysis',
  data: {
    names: [],
    zoom_id: '',
    speaking_im_b64: '',
    particular_name: '',
    res: {},
    prechart: undefined,
  },
  methods: {
    evaluationSet: function () {
      axios
        .post('/api/set-evaluation', {
          zoom_id: this.zoom_id,
        })
        .then((response) => {
          this.names = Object.keys(response.data.res);
          this.res = response.data.res;
          console.log(this.names);
          console.log(response.data.res);
        });
    },
    evaluationDisplay: function (name) {
      const partres = this.res[name];
      this.speaking_im_b64 = partres.speaking_im_b64;

      var cop = {
        type: 'doughnut',
        data: {
          labels: [
            'angry',
            'disgust',
            'fear',
            'happy',
            'neutral',
            'sad',
            'surprise',
          ],
          datasets: [
            {
              label: '# frames',
              data: [
                partres.angry,
                partres.disgust,
                partres.fear,
                partres.happy,
                partres.neutral,
                partres.sad,
                partres.surprise,
              ],
              backgroundColor: [
                'rgba(146,  43, 150)',
                'rgba(197,  43,  46)',
                'rgba(250, 226,  78)',
                'rgba(246, 180, 194)',
                'rgba(100, 184,  99)',
                'rgba(176, 210, 211)',
                'rgba(224,  33, 120)',
              ],
              hoverOffset: 4,
            },
          ],
        },
      };
      if (window.emotionChart) window.emotionChart.destroy();
      window.emotionChart = new Chart('emotion-chart', cop);
    },
  },
});
