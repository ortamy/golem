import fs from 'fs'
const f = 'c:\\Users\\DELL\\Desktop\\golem-main\\products\\website\\apps\\researchlab\\js\\learn.js'
let s = fs.readFileSync(f, 'utf8')

// L115: заменяем <h1> на <div class="learn-lesson-title"> в renderLesson
const before = "<h1>' + esc(item.name) + '</h1>"
const after  = "<div class=\"learn-lesson-title\">' + esc(item.name) + '</div>"
if (s.includes(before)) {
  s = s.replace(before, after)
  console.log('learn.js: L115 h1->div OK')
} else {
  console.log('learn.js: NOT FOUND')
}

fs.writeFileSync(f, s, 'utf8')


