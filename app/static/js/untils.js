function debounce(fn, wait) {
    let timeout = null
    return function() {
        const context = this
        const args = arguments
        clearTimeout(timeout)
        timeout = setTimeout(()=>{fn.apply(context, args)}, wait)
    }

}

function throttle(fn, wait) {
    let controller
    return function() {
        const context = this
        const args = arguments
        if (!controller) {
            fn.apply(context, args)
            controller = true
            setTimeout(()=>{
                controller = false
            }, wait)
        }
    }
}

export {debounce, throttle}