import {throttle} from './untils.js'

function gotop_arrow() {
    document.onscroll = throttle((e) => {
        console.log(window.scrollY)
    }, 200)
}

export {gotop_arrow}