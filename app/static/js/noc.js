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

let noc_alert = (() => {
    let length = 0;
    return function noc_alter(message, category = CATEGORY_TYPES.PRIMARY, max_length = 3) {
        (() => {
            let alert_place = document.querySelector('#alert-placeholder')
            category = CATEGORY_TYPES[category] || category;
            let inner_html = `
                <div class="alert alert-${category} alert-dismissible fade show" role="alert" id="noc-alert-${length}">
                    <strong>${message}!</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`
            if(length < max_length) {
                length++
            } else {
                alert_place.removeChild(alert_place.firstElementChild)
            }
            alert_place.innerHTML = alert_place.innerHTML.concat(inner_html)
        })()
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

function get_system_messages(index=null, fn) {
    fetch(location.origin+`/messages/${index}`, {
        headers: {
            'N-From-Fetch': 1
        }
    }).then((res) => {return res.json()}).then((res) => {
        console.log(res)
        fn(res)
    })
}

export {gotop_arrow, noc_alert, noc_highlight, get_system_messages}