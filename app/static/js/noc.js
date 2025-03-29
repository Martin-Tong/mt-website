import {throttle} from './untils.js'

function gotop_arrow() {
    let _initial = 0
    const _gotop = document.querySelector('#gotop')
    _gotop.addEventListener('click', () => {
            window.scrollTo({
                top:0,
                behavior: 'smooth'
            }
        )
    })
    document.onscroll = throttle((e) => {
        let _scrolly = window.scrollY
        if ((_scrolly - _initial) < 0 && _scrolly > 400) {
            _gotop.style.scale = 1
        } else {
            _gotop.style.scale = 0
        }
        _initial = _scrolly
    }, 100)
}

const CATEGORY_TYPES = {
    PRIMARY: 'primary',
    SUCCESS: 'success',
    DANGER: 'danger',
    WARNING: 'warning',
};

let noc_toast = (() => {
    let length = 0;
    return function not_toast(message, category = CATEGORY_TYPES.PRIMARY, max_length = 3) {
        let toast_place = document.querySelector('#toast-placeholder')
        category = CATEGORY_TYPES[category] || category;
        let inner_html = `
            <div class="toast align-items-center text-white bg-${category} border-0" id="noc-toast-${length}">
               <div class="toast-header bg-${category}">
                  <strong class="me-auto">新的系统信息</strong>
                  <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
               </div>
               <div class="toast-body text-truncate">
                   ${message}
               </div>
            </div>`
        if(toast_place.hasChildNodes() && toast_place.childElementCount >= max_length) {
            toast_place.removeChild(toast_place.firstElementChild)
        }
        length += 1
        toast_place.innerHTML = toast_place.innerHTML.concat(inner_html)
        let toast = new bootstrap.Toast(document.querySelector(`#noc-toast-${length-1}`))
        toast.show()
    }
})()
let noc_alert = (() => {
    let length = 0;
    return function noc_alter(message, category = CATEGORY_TYPES.PRIMARY, fixed = false, max_length = 3) {
        let alert_place = document.querySelector('#alert-placeholder')
        category = CATEGORY_TYPES[category] || category;
        let inner_html = `
                <div class="alert alert-${category} alert-dismissible fade show ${fixed?'fixed':''}" role="alert" id="noc-alert-${length}">
                    <strong>${message}!</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`
        if(alert_place.hasChildNodes() && alert_place.childElementCount >= max_length) {
            alert_place.removeChild(alert_place.firstElementChild)
        }
        length += 1
        alert_place.innerHTML = alert_place.innerHTML.concat(inner_html)
    }
})()


/**
 * 根据当前选择对指定DOM目标中的文本应用突出显示。
 *
 * 此函数设置一个回调，当调用该回调时，将突出显示当前对象的所有出现在目标元素中的选定文本。它使用‘ Range ’，’ HighLight ‘和‘ TreeWalker ’ DOM api来查找和突出显示与所选内容匹配的文本节点。
 *
 * @param {string} target - 一个CSS选择器字符串，用于定位应该高亮显示的DOM元素。
 * @return {Function} 处理目标元素触发选择行为时的事件函数
 */
function noc_highlight(target) {
    let _target = document.querySelector(target)
    _target.addEventListener('dblclick', () => {
        CSS.highlights.clear()
    })
    let nodes = document.createTreeWalker(_target, NodeFilter.SHOW_TEXT, null)
    let textnodes = []
    while (nodes.nextNode()) {
        textnodes.push(nodes.currentNode)
    }
    return function () {
        CSS.highlights.clear()
        let e = arguments[0] //事件对象
        let section = e.target.value.substring(e.target.selectionStart, e.target.selectionEnd) //选择的字符串
        const ranges = textnodes.map(node => {
            return {node, text: node.textContent}
        }).map(({node, text}) => {
            const index = []
            let start = 0
            while (start < text.length) {
                const i = text.indexOf(section, start)
                if (i === -1) break
                index.push(i)
                start = i + section.length
            }
            return index.map((i) => {
                const range = new Range()
                range.setStart(node, i)
                range.setEnd(node, i + section.length)
                return range
            })
        })
        const searchResult = new Highlight(...ranges.flat())
        CSS.highlights.set('searchResult', searchResult)
    }
}

 async function get_system_messages() {
     let _i = await fetch(location.origin+`/messages`, {
        headers: {
            'N-From-Fetch': 1
        },
        withCredentials: 'same-origin'
    })
     return await _i.json()
}

class SystemMessage {
    constructor(message) {
        this.message = message
    }
    static async init() {
        let _data = sessionStorage.getItem('system_message')
        if (_data) {
            return new SystemMessage(JSON.parse(_data))
        }
        let data = await get_system_messages()
        if (data.status === 'success') {
            let _i = new SystemMessage(data.message)
            _i.setLocalCache(data.message)
            return _i
        }
        return new SystemMessage('null')
    }
    setLocalCache(data) {
        let _origin = sessionStorage.getItem('system_message')
        if (!_origin || JSON.stringify(data) !== _origin) {
            _origin = _origin || '{}'
            let _keys = Object.keys(data)
            let _diff = _keys.filter((key) => {
                return !Object.keys(JSON.parse(_origin)).includes(key)
            })
            noc_toast(`您有${_diff.length}条新的系统消息`, 'primary')
        }
        sessionStorage.setItem('system_message', JSON.stringify(data))
        this.message = data
        return this
    }
    clearLocalCache() {
        sessionStorage.removeItem('system_message')
        this.message = 'null'
        return this
    }
    updateLocalCache() {
        let _this = this
        setInterval(async () => {
            let data = await get_system_messages()
            if (data.status === 'success') {
                _this.setLocalCache(data.message)
            } else {
                _this.clearLocalCache()
            }
            _this.handle()
        }, 1000*30)
    }
    // 处理消息
    handle() {
        let _inner = document.querySelector('#noc-sys-message')
        let _outer = document.querySelector('#noc-user-dropdown')
        let _html = '信息'
        if (this.message !== 'null') {
            let _length = Object.keys(this.message).length
            _inner.innerHTML = _html.concat(`&nbsp;&nbsp;<span class="badge text-bg-primary rounded-pill">${_length}</span>`)
            _outer.dataset.hasMessage = 'true'
        } else {
            _inner.innerHTML = _html
            _outer.dataset.hasMessage = 'false'
        }
    }
}

export {gotop_arrow, noc_alert, noc_toast, noc_highlight, SystemMessage}