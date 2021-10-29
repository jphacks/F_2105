Vue.use(VeeValidate, {
  locale: 'ja',
  events: 'input|blur|focus'
});

Vue.component('listitem', {
  props: ['item','index'],
  inject: ['$validator'], //Validetaionを共有
  data: function () {
    return {
      // プルダウン
      PulldownInitialMessage: '選択してください',
      inputvalue: this.item.initialvalue ? this.item.initialvalue : null,
      inputvalues: Array.isArray(this.item.options) ? [] : false
    }
  },
  computed: {
    options_with_freeanswer: function() {
      var options = this.item.options
      if(this.item.freeanswer && Array.isArray(options)) {
        return options.concat(['__other_option__'])
      } else if(!Array.isArray(options)){
        return [options]
      } else {
        return options
      }
    }
  },
  methods: {
    check: function(id){
      var target = document.getElementById(id);
      if(!target.checked) target.click() // IDのclick
    },
    focus: function(textid, checkboxid) {
      if(!checkboxid || document.getElementById(checkboxid).checked) {
        document.getElementById(textid).focus()
      }
    }
  },
  template: /* HTML */`
  <div class="form-group" :class="{'has-error': errors.has('entry.'+item.name) || errors.has('entry.'+item.name+'.other_option_response')}">
    <label class="form-label" :for="'entry.'+item.name">{{item.question}}</label>

    <template v-if="item.questiontype === 'text'">
      <input
      class="form-input"
      type="text"
      :area-label="item.question"
      :id="'entry.'+item.name" :name="'entry.'+item.name" :data-vv-as="item.question"
      v-model="inputvalue"
      v-validate="item.validate === true ? 'required' : item.validate"
      :placeholder="item.placeholder">
    </template>

    <template v-else-if="item.questiontype === 'textarea'">
      <textarea
      class="form-input"
      :id="'entry.'+item.name" :name="'entry.'+item.name" :data-vv-as="item.question"
      v-model="inputvalue"
      v-validate="item.validate === true ? 'required' : item.validate"
      :placeholder="item.placeholder">
      </textarea>
    </template>

    <template v-else-if="item.questiontype === 'radio'">
      <div class="input-group" v-for="(option, ansnum) in options_with_freeanswer">
        <label
        class="form-radio"
        @click="if(option === '__other_option__') focus('entry.'+item.name+'.other_option_response')">
          <input
          type="radio"
          :id="'q'+index+'_a'+ansnum"
          :name="'entry.'+item.name" :data-vv-as="item.question"
          :value="option"
          v-model="inputvalue"
          v-validate="item.validate === true ? 'required' : item.validate">
          <i class="form-icon"></i>
          <span>{{option !== '__other_option__' ? option : item.freeanswer}}</span>
        </label>
        <input
        v-if="option === '__other_option__'"
        type="text" class="form-input"
        :id="'entry.'+item.name+'.other_option_response'"
        :name="'entry.'+item.name+'.other_option_response'" :data-vv-as="item.question"
        v-validate="(item.validate === true ? 'required' : item.validate) && inputvalue == '__other_option__' ? 'required' : false"
        @input="check('q'+index+'_a'+ansnum)" @click="check('q'+index+'_a'+ansnum)">
      </div>
    </template>

    <template v-else-if="item.questiontype === 'checkbox'">
      <div class="input-group" v-for="(option, ansnum) in options_with_freeanswer">
        <label :class="Array.isArray(item.options) ? 'form-checkbox' : 'form-switch'">
          <input
          type="checkbox" :id="'q'+index+'_a'+ansnum"
          :name="'entry.'+item.name" :data-vv-as="item.question"
          :value="Array.isArray(item.options) ? option : inputvalues"
          v-model="inputvalues"
          v-validate="item.validate === true ? 'required' : item.validate"
          @click="if(option === '__other_option__') focus('q'+index+'_freeanswer', 'q'+index+'_a'+ansnum)">
          <i class="form-icon"></i>
          <span>{{option !== '__other_option__' ? option : item.freeanswer}}</span>
        </label>
        <input
        v-if="option === '__other_option__'"
        type="text" class="form-input"
        :id="'q'+index+'_freeanswer'"
        :name="'entry.'+item.name+'.other_option_response'" :data-vv-as="item.question"
        v-validate="item.validate && inputvalues.includes('__other_option__') ? 'required' : false"
        @input="check('q'+index+'_a'+ansnum)" @click="check('q'+index+'_a'+ansnum)">
      </div>
    </template>

    <template v-else-if="item.questiontype === 'pulldown'">
      <select class="form-select" v-model="inputvalue"
      :id="'entry.'+item.name" :name="'entry.'+item.name" :data-vv-as="item.question"
      v-validate="item.validate === true ? 'required' : item.validate">
        <option disabled value="">{{PulldownInitialMessage}}</option>
        <option v-for="(option, index) in item.options" :value="option">{{option}}</option>
      </select>
    </template>

    <p v-if="errors.has('entry.'+item.name) || errors.has('entry.'+item.name+'.other_option_response')"" class="form-input-hint">
      <template v-if="errors.has('entry.'+item.name)">{{ errors.first('entry.'+item.name) }}</template>
      <template v-else>{{ errors.first('entry.'+item.name+'.other_option_response') }}</template>
    </p>
  </div>`
});

var contact = new Vue({
  el: '#contact',
  data: {
    formdata: {},
    submitted: false
  },
  methods: {
    gf_submit: function() {
      this.$validator.validate().then(result => {
        if (!result) {
          return false;
        }
        document.gf_form.submit();
        this.submitted = true;  
      });
    }
  },
  mounted: function() {
    var iframe = document.createElement("iframe");
    iframe.setAttribute('name','hidden_iframe');
    iframe.setAttribute('style','display: none');
    document.body.appendChild(iframe);
  }
});