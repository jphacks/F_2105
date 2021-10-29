// 参考：https://github.com/ytr0903/google-form-with-vue

/*
<使い方>
1.Google Formでフォームを作成
2.フォーム画面からname, actionをコピー
3.vue-gf-data.jsのdocに設問・選択肢を入力
4.必要なCSS・JSをCDNで読み込む
*/

contact.formdata = {
  doc: 'https://docs.google.com/forms/u................./formResponse',  // ここに入力
  survey: [
    {
      name: 631244584, // ここに入力 10桁
      question: '名前',
      questiontype: 'text',
      label: 'username',
      validate: 'required'
    },
    {
      name: 209524638, // ここに入力 10桁
      question: 'メールアドレス',
      questiontype: 'text',
      label: 'email',
      placeholder: 'xxxxx@example.com',
      validate: 'required|email'
    },
    {
      name: 529582982, // ここに入力 10桁
      question: '電話番号',
      questiontype: 'text',
      placeholder: '0123456789',
      validate: 'required|numeric'
    },
    {
      name: 1800031148, // ここに入力 10桁
      question: '会社名・団体名',
      questiontype: 'text',
      label: 'company',
      validate: 'required'
    },
    {
      name: 2072623167, // ここに入力 10桁
      question: 'お問い合わせ内容',
      questiontype: 'textarea',
      validate: 'required'
    },
  ]
}