/**
 * avatar-stack.js — общий компонент стека аватарок.
 * Используется в карточках клуба, детали и сайд-панели.
 */

function renderAvatarStack(users, max) {
  max = max || 5;
  if (!users || !users.length) return '';
  var visible = users.slice(0, max);
  var remaining = users.length - max;
  var html = '<div class="avatar-stack">';
  visible.forEach(function(user, i) {
    html += '<button type="button" class="avatar-circle" data-profile="' + i + '" style="background:' + (user.color || '#b8860b') + ';margin-left:' + (i === 0 ? '0' : '-8px') + ';" title="Профиль ' + (user.handle || '') + '">' + (user.initial || '?') + '</button>';
  });
  if (remaining > 0) {
    html += '<span class="avatar-circle avatar-more" style="margin-left:-8px;">+' + remaining + '</span>';
  }
  html += '</div>';
  return html;
}

window.renderAvatarStack = renderAvatarStack;
