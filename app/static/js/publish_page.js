import { noc_highlight} from "./noc.js";
import {attach_event, throttle} from "./untils.js"


attach_event('#flask-pagedown-content', 'select', (e) =>{
    if (CSS.highlights) {
        noc_highlight('#flask-pagedown-content-preview')(e)
    }
})

let _html = `<div id="content-controller" class="d-none d-lg-block">
            <button class="btn" title="锁定文本框" type="button" id="content-controller_lock" data-locked="false">
              <i class="bi bi-unlock"></i>
            </button>
            <button class="btn" title="查看markdown语法" type="button" id="content-controller_md" data-bs-toggle="offcanvas" data-bs-target="#offcanvasRight">
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

function lock_mousedown(e) {
    let target = document.querySelector("#flask-pagedown-content")
    if (!(e.target == target)) {
        e.preventDefault()
        e.stopPropagation()
    }
}

//锁定时阻止tab、alt键切换聚焦状态以及其他快捷键
function lock_keydown(e) {
    if (['Tab', 'Alt'].indexOf(e.key) != -1) {
        e.preventDefault()
        e.stopPropagation()
        if (e.key == 'Tab') {
            let target = document.querySelector("#flask-pagedown-content")
            target.value += '    '
        }
    } else  {
        if (e.ctrlKey && e.key.toLocaleLowerCase() == 'i') {
            upload_image(e)
        }
    }
}
// 上传图片
function upload_image(e) {
    e.preventDefault()
    e.stopPropagation()
    let _input = document.createElement('input')
    _input.type = 'file'
    _input.accept = 'image/png, image/jpeg, image/gif, image/jpg'
    _input.addEventListener('change', (e) => {
        let file = e.target.files[0]
        let formdata = new FormData()
        let xhr = new XMLHttpRequest()
        formdata.append('file', file)
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                let _progress = document.querySelector('#flask-pagedown-upload-progress')
                _progress.style.width = `${e.loaded / e.total * 100}%`
            }
        })
        xhr.onload = (e) => {
            let _content = document.querySelector('#flask-pagedown-content')
            let _progress = document.querySelector('#flask-pagedown-upload-progress')
            _progress.style.width = 0
            let _start = _content.selectionStart
            let _end = _content.selectionEnd
            let _value = _content.value
            _content.value = _value.slice(0, _start) + `\n\n![${file.name}](`+JSON.parse(e.target.response).path+')\n\n' + _value.slice(_end)
            _input = null
            xhr = null
        }
        xhr.withCredentials = true
        xhr.open('POST', 'http://127.0.0.1:5555/upload/', true)
        xhr.send(formdata)
    })
    _input.addEventListener('cancel', (e) => {
      _input = null
    })
    _input.addEventListener('error', (e) => {
        _input = null
    })
    _input.addEventListener('abort', (e) => {
        _input = null
    })
    _input.click()
}
//点击🔒按钮事件
function lock_event(e) {
    let target = document.querySelector("#flask-pagedown-content")
    let eventtarget = e.currentTarget
    let locked = eventtarget.dataset.locked == 'false'
    let icon = lock_change(eventtarget)
    let _nav = document.querySelector('nav')
    let _submit = document.querySelector('#post_submit')
    if (locked) {
        // locked
        target.focus()
        icon.title = '解锁文本框'
        _nav.classList.add('pe-none')
        _submit.classList.add('pe-none')
        document.addEventListener('click', lock_click, true)
        document.addEventListener('mousedown', lock_mousedown, true)
        target.addEventListener('keydown', lock_keydown)
    } else {
        target.blur()
        icon.title = '锁定文本框'
        _nav.classList.remove('pe-none')
        _submit.classList.remove('pe-none')
        document.removeEventListener('click', lock_click, true);
        document.removeEventListener('mousedown', lock_mousedown, true);
        target.removeEventListener('keydown', lock_keydown)
    }
}
//处理输入时出现滚动条
function scroll_show_event(mutationList, observer) {
    let _windowHeight = window.innerHeight
    let _pageHeight = document.querySelector('html').offsetHeight
    if (_pageHeight > _windowHeight) {
        window.scrollTo({behavior: 'smooth', top: _pageHeight - _windowHeight})
        }
}
let _md_preview = document.querySelector('#flask-pagedown-content-preview')
let _md_preview_observer = new MutationObserver(scroll_show_event)
_md_preview_observer.observe(_md_preview, {attributes: true, childList: true, subtree: true})

attach_event('#content-controller_lock', 'click', lock_event)

window.addEventListener('unload', ()=>{
    _md_preview_observer.disconnect()
    _md_preview_observer = null
})