// 노트북 에디터(CodeMirror 6) 번들 진입점
// npm run build:vendor 로 assets/vendor/codemirror.js 를 다시 만듭니다.
export { EditorView, keymap, Decoration } from '@codemirror/view';
export { EditorState, Prec, StateField, StateEffect } from '@codemirror/state';
export { basicSetup } from 'codemirror';
export { indentWithTab } from '@codemirror/commands';
export {
    indentUnit,
    HighlightStyle,
    syntaxHighlighting,
} from '@codemirror/language';
export { python, pythonLanguage } from '@codemirror/lang-python';
export { completeFromList } from '@codemirror/autocomplete';
export { tags } from '@lezer/highlight';
