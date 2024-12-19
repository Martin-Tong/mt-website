!(() => {
    let check_storage_useful = (() => {
        return (type) => {
            let x = '__test_data__'
            var storage
            try {
                storage = window[type]
                storage.setItem(x, x)
                storage.getItem(x)
                storage.removeItem(x)
                this._local_support = true
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
        let scheme_target = document.querySelector('html[lang="zh-CN"]')
        scheme_target.dataset['bsTheme'] = theme
    }

    window.addEventListener('DOMContentLoaded', () => {
        let dark = window.matchMedia('(prefers-color-scheme:dark)').matches
        let controller = document.querySelector('#theme-control button')
        let scheme_target = document.querySelector('html[lang="zh-CN"]')
        if (check_storage_useful('localStorage')) {
            if (!localStorage.getItem('scheme')) {
                localStorage.setItem('scheme', dark?'dark':'light')
            }
            change_theme(localStorage.getItem('scheme'))
            controller.addEventListener('click', ()=>{
                let _scheme = localStorage.getItem('scheme')
                _scheme == 'dark'?change_theme('light'): change_theme('dark')
                localStorage.setItem('scheme', _scheme == 'dark'?'light':'dark')
            })
        }else {
            scheme_target.dataset['bsTheme'] = dark?'dark':'light'
        }
    }, true)
})()