import fs from 'fs'

const f = 'c:\\Users\\DELL\\Desktop\\golem-main\\products\\website\\apps\\researchlab\\js\\paleo-linguistics.js'
let s = fs.readFileSync(f, 'utf8')

const before = '\'<h1><img src="../../assets/icons/32/scribe/scroll.png" class="lab-icon" alt="">\' + escapeHtml(lang.name) + \'</h1>\' +'
const after  = '\'<div class="pl-lang-title-wrap"><img src="../../assets/icons/32/scribe/scroll.png" class="lab-icon" alt="">\' + escapeHtml(lang.name) + \'</div>\' +'

if (s.includes(before)) {
  s = s.replace(before, after)
  fs.writeFileSync(f, s, 'utf8')
  console.log('OK paleo-linguistics h1->div')
} else {
  console.log('NOT FOUND')
}
