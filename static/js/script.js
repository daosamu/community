// 页面加载完成后执行的函数
window.onload = function () {
    // 示例：点击文章标题时，添加一个类来改变样式（模拟交互效果）
    var articleTitles = document.querySelectorAll('.article h3 a');
    articleTitles.forEach(function (title) {
        title.addEventListener('click', function () {
            this.classList.add('active');
        });
    });
    // 示例：点击导航栏链接时，添加/移除 active 类来改变样式（模拟交互效果）
    var navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            navLinks.forEach(function (navLink) {
                navLink.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
};