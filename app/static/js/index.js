import {gotop_arrow, noc_alert, noc_toast, SystemMessage} from './noc.js'

gotop_arrow()
if (noc_user_status) {
    window._noc_message = await SystemMessage.init()
    if (window._noc_message) {
        window._noc_message.handle()
        window._noc_message.updateLocalCache()
    }
    window.addEventListener('beforeunload', () => {
        window._noc_message = null
    })
}
window._noc_utils={noc_alert, noc_toast}