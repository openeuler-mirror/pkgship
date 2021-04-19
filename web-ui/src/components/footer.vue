<template>
    <div class="footer-wrapper">
        <div class="footer-content">
            <div class="footer-left">
                <a href="https://gitee.com/openeuler/pkgship" target="_blank">
                    <img src="@/assets/images/pkgLogo.svg" class="footer-logo">
                </a>
            </div>
            <div class="footer-right">
                <ul class="right-list">
                    <li v-for="(item, index) in footer.rightList" :key="index"><a :href="item.link" target="_blank">{{ item.name }}</a></li>
                </ul>
                <p class="footer-copyright">{{ footer.copyright }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            footer: {
                leftLogo: 'openEuler',
                mail: 'contact@openeuler.org',
                copyright: '版权所有 © 2020 openeuler 保留一切权利',
                rightList: [
                    {
                        name: 'Trademark',
                        link: 'https://openeuler.org/en/other/brand/'
                    },
                    {
                        name: 'Legal Notice',
                        link: 'https://openeuler.org/en/other/legal/'
                    },
                    {
                        name: 'Privacy Policy',
                        link: 'https://openeuler.org/en/other/privacy/'
                    }]
            }
        };
    },
    components: {}
};
</script>

<style lang="less" scoped>
.footer-wrapper {
    height: 176px;
    background-color: #111;
    @media (max-width: 1000px) {
        height: 280px;
    }
    .footer-content {
        .ff-xih();
        margin: 0 auto;
        height: 100%;
        width: 1200px;
        display: flex;
        justify-content: space-between;
        @media (max-width: 1000px) {
            flex-direction: column;
            align-items: center;
            width: 100%;

        }
        .footer-left {
            @media (max-width: 1000px) {
                height: 50%;
            }
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            .fz16();
            .footer-mail {
                color: @text-white;
                margin-top: 17px;
            }
        }
        .footer-right {
            @media (max-width: 1000px) {
                height: 50%;
                align-items: unset;
                padding-bottom: 67px;
            }
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-end;
            .footer-copyright {
                color: #fff;
                margin-top: 21px;
                .fz12();
            }
            .right-list {
                display: flex;
                align-items: flex-end;
                .fz14();
                li {
                    padding: 0 15px;
                    a {
                        color: #fff;
                        text-decoration: none;
                    }
                }
                li:nth-child(2){
                    padding: 0 16px;
                    border-left: 1px solid #fff;
                    border-right: 1px solid #fff;
                }
                li:nth-child(3){
                    padding-right: 0;
                }
            }
        }
    }
}
</style>
