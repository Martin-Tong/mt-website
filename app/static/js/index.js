import {gotop_arrow, noc_alert, get_system_messages} from './noc.js'

function show_system_message(data) {
    switch (data.message) {
        case 'need-confirmation':
            noc_alert('当前用户需要验证邮箱', 'warning')
            return
    }
}

gotop_arrow()
//get_system_messages('need-confirmation', show_system_message)
window._noc_utils={noc_alert}