(() => {
'use strict'

let check_storage_useful = (() => {
    return (type) => {
        let x = '__test_data__'
        var storage
        try {
            storage = window[type]
            storage.setItem(x, x)
            storage.getItem(x)
            storage.removeItem(x)
            storage.clear()
            return true
        } catch (e) {
            return (
                e instanceof DOMException && (
                    e.code === 22 || e.code === 1014 || e.name === "QuotaExceededError" || e.name === "NS_ERROR_DOM_QUOTA_REACHED") && storage
                )
        }
    }
})()

function change_theme(theme) {
    let scheme_tatget = document.querySelector('html[lang="zh-CN"]')
    scheme_tatget.dataset['bsTheme'] = theme
    localStorage.setItem('scheme', theme)
}

window.addEventListener('DOMContentLoaded', () => {
    let dark = window.matchMedia('(prefers-color-scheme:dark)').matches
    let controller = document.querySelector('#theme-control button')
    if (check_storage_useful('localStorage')) {
        localStorage.setItem('scheme', dark?'dark':'light')
    }
    if (dark) {
        change_theme('dark')
    } else {
        change_theme('light')
    }
    controller.addEventListener('click', ()=>{
        let _scheme = localStorage.getItem('scheme')
        _scheme == 'dark'?change_theme('light'): change_theme('dark')
    })
})

})()