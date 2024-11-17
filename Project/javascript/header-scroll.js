window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled'); // إضافة كلاس "scrolled" عند التمرير
    } else {
        header.classList.remove('scrolled'); // إزالة الكلاس عند الرجوع لأعلى
    }
});
