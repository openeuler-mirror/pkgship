<template>
    <div class="footer-wrapper">
        <div class="atom">
            <p>{{ footer.atomText }}</p>
            <img src="@/assets/images/atom.png" alt="">
        </div>
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
                atomText:'openEuler 是由开放原子开源基金会（OpenAtom Foundation）孵化及运营的开源项目',
                leftLogo: 'openEuler',
                mail: 'contact@openeuler.org',
                copyright: '版权所有 © 2022 openeuler 保留一切权利',
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
    height: 490px;
    background-color: #111;
    @media (max-width: 1000px) {
        height: 460px;
    }
    .atom {
        height: 330px;
        text-align: center;
        overflow: hidden;
        img {
          width: 380px;
          height: 81px;
        }
        p {
          margin: 88px 0 50px 0;
          color: #fff;
          font-size: 20px;
        }
    }
    @media screen and (max-width: 1000px) {
     .atom {
      padding: 0 50px;
      height: 180px;
      img {
        width: 191px;
        height: 41px;
      }
      p {
        font-size: 12px;
        margin: 40px 0 20px 0;
      }
     }
    }
    .footer-content {
        .ff-xih();
        margin: 0 auto;
        width: 1200px;
        display: flex;
        justify-content: space-between;
        @media (max-width: 1000px) {
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 280px;
        }
        .footer-left {
            @media (max-width: 1000px) {
                height: 50%;
            }
            height: 160px;
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
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-end;
            .footer-copyright {
                text-align: center;
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
