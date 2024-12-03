import { noc_highlight} from "./noc.js";
import {attach_event} from "./untils.js"


attach_event('#flask-pagedown-content', 'select', (e) =>{
    if (CSS.highlights) {
        noc_highlight('#flask-pagedown-content-preview')(e)
    }
})

let _html = `<div id="content-controller" class="d-none d-lg-block">
            <button class="btn" title="锁定文本框" type="button" id="content-controller_lock" data-locked="false">
              <i class="bi bi-unlock"></i>
            </button>
            <button class="btn" title="查看markdown语法" type="button" id="content-controller_md">
              <i class="bi bi-filetype-md"></i>
            </button>
          </div>`
document.querySelector('.flask-pagedown').insertAdjacentHTML('afterbegin', _html)

//切换锁定按钮的图标
function lock_change(eventtarget) {
    let locked = eventtarget.dataset.locked
    let icon = eventtarget.querySelector('i')
    icon.classList = (icon.classList == 'bi bi-lock' ? 'bi bi-unlock' : 'bi bi-lock')
    eventtarget.dataset.locked= locked == 'false' ? 'true' : 'false'
    return icon
}

//锁定时组织输入框外的点击事件
function lock_click(_e) {
    let eventtarget = document.querySelector('#content-controller_lock')
    let icon = eventtarget.querySelector('i')
    let target = document.querySelector("#flask-pagedown-content")
    if (_e.target == eventtarget || _e.target == icon) {
    } else {
        _e.preventDefault()
        _e.stopPropagation()
        target.focus()
    }
}

//锁定时组织tab、alt键切换聚焦状态
function lock_keydown(e) {
    if (['Tab', 'Alt'].indexOf(e.key) != -1) {
        e.preventDefault()
        e.stopPropagation()
    }
}

function lock_event(e) {
    let target = document.querySelector("#flask-pagedown-content")
    let eventtarget = e.currentTarget
    let locked = eventtarget.dataset.locked == 'false'
    let icon = lock_change(eventtarget)
    if (locked) {
        // locked
        target.focus()
        icon.title = '解锁文本框'
        document.addEventListener('click', lock_click, true)
        document.addEventListener('mousedown', lock_click, true)
        target.addEventListener('keydown', lock_keydown)
    } else {
        target.blur()
        icon.title = '锁定文本框'
        document.removeEventListener('click', lock_click, true);
        document.removeEventListener('mousedown', lock_click, true);
        target.removeEventListener('keydown', lock_keydown)
    }
}
attach_event('#content-controller_lock', 'click', lock_event)