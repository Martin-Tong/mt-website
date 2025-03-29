/**
 * Debounce function to delay the execution of a function until after a specified wait time has elapsed
 * since the last time it was invoked.
 *
 * @param {Function} fn - The function to be debounced.
 * @param {number} wait - The time interval in milliseconds to wait before invoking the function.
 * @returns {Function} - A debounced version of the input function.
 */
function debounce(fn, wait) {
    let timeout = null
    return function() {
        const context = this
        const args = arguments
        clearTimeout(timeout)
        timeout = setTimeout(()=>{fn.apply(context, args)}, wait)
    }

}
/**
 * Throttle function to limit the execution of a function to once every specified time interval.
 *
 * @param {Function} fn - The function to be throttled.
 * @param {number} wait - The time interval in milliseconds to wait before allowing the function to be called again.
 * @returns {Function} - A throttled version of the input function.
 */
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

function attach_event(target,event_name, fn) {
    const _target = document.querySelector(target)
    _target.addEventListener(event_name, fn)
    window.addEventListener('unload', () => {
        _target.removeEventListener(event_name, fn)
    })
}

export {debounce, throttle, attach_event}