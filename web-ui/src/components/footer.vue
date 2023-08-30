<template>
  <div class="footer">
    <div class="atom">
      <p class="atom-text">
        {{ atomText }}
      </p>
      <a href="https://openatom.cn" target="_blank">
        <img src="@/assets/images/atom-logo.svg" class="atom-logo" alt="" />
      </a>
    </div>
    <div class="footer-content">
      <div class="inner">
        <div class="footer-logo">
          <img class="show-pc" src="@/assets/images/footer-logo2.png" alt="" />
          <p>
            <a class="email" href="mailto:contact@openeuler.io" target="_blank">
              {{ mail }}
            </a>
          </p>
        </div>
        <div class="footer-option">
          <div class="footer-option-item">
            <a
              v-for="link in rightList"
              :key="link.URL"
              href="javascript:;"
              class="link"
              @click="handleNavClick(link.URL)"
              >{{ link.NAME }}</a
            >
          </div>
          <p class="copy-right">
            {{ copyright }}
          </p>
          <p class="license">
            <span>Licensed under</span>
            the MulanPSL2
          </p>
        </div>
        <div class="footer-right">
          <div class="footer-links">
            <a
              v-for="item in linksData"
              :key="item.id"
              :href="item.path"
              class="links-logo"
              target="_blank"
            >
              <img :src="item.logo" alt="" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LogoRedditSquare from '@/assets/images/reddit-square@2x.png';
import LogoBilibili2 from '@/assets/images/bilibili@2x.png';
import LogoLinkedin from '@/assets/images/linkedin@2x.png';
import LogoYoutube from '@/assets/images/youtube@2x.png';
import LogoTwitter from '@/assets/images/twitter@2x.png';
export default {
  data() {
    return {
      atomText:
        ' openEuler is an open source project incubated and operated by the OpenAtom Foundation.',
      leftLogo: 'openEuler',
      mail: 'contact@openeuler.org',
      copyright: 'Copyright © 2023 openEuler. All rights reserved.',
      rightList: [
        {
          NAME: 'Trademark',
          URL: 'https://www.openeuler.org/en/other/brand/',
        },
        {
          NAME: 'Privacy Policy',
          URL: 'https://www.openeuler.org/en/other/privacy/',
        },
        {
          NAME: 'Legal Notice',
          URL: 'https://www.openeuler.org/en/other/legal/',
        },
        {
          NAME: 'Service Status',
          URL: 'https://status.openeuler.org/',
        },
      ],
      linksData: [
        {
          path: 'https://www.reddit.com/r/openEuler/',
          logo: LogoRedditSquare,
          id: 'reddit-square',
        },
        {
          path: 'https://www.linkedin.com/company/openeuler',
          logo: LogoLinkedin,
          id: 'linkedin',
        },
        {
          path: 'https://twitter.com/openEuler',
          logo: LogoTwitter,
          id: 'twitter',
        },
        {
          path: 'https://space.bilibili.com/527064077/channel/series',
          logo: LogoBilibili2,
          id: 'bilibili',
        },
        {
          path: 'https://www.youtube.com/channel/UCPzSqXqCgmJmdIicbY7GAeA',
          logo: LogoYoutube,
          id: 'youtube',
        },
      ],
    };
  },
  components: {},
  methods: {
    handleNavClick: (path) => {
      if (path.startsWith('https:')) {
        window.open(path, '_blank');
      }
    },
  },
};
</script>

<style lang="less" scoped>
.footer {
  background: var(--o-color-greyblack1);
  .atom {
    text-align: center;
    padding: var(--o-spacing-h3) 0 var(--o-spacing-h4);
    position: relative;
    border-bottom: 1px solid rgba(229, 229, 229, 0.12);
    @media (max-width: 1440px) {
      padding: var(--o-spacing-h4) 0;
    }

    &-text {
      font-size: var(--o-font-size-h6);
      font-weight: 400;
      color: #fff;
      line-height: var(--o-line-height-h6);
      @media (max-width: 1440px) {
        font-size: var(--o-font-size-text);
        line-height: var(--o-line-height-text);
      }
    }
    &-logo {
      height: 48px;
      margin-top: 16px;
      @media (max-width: 1100px) {
        height: 38px;
      }
    }
  }

  &-content {
    padding-left: 44px;
    padding-right: 44px;
    max-width: 1288px;
    margin: 0 auto;
    background: url(../assets/images/footer-bg.png) no-repeat bottom center;
    .inner {
      display: flex;
      align-items: end;
      justify-content: space-between;
      padding: 18px 0 32px;
      position: relative;
      min-height: 118px;
      @media (max-width: 1400px) {
        padding: var(--o-spacing-h4) 0;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
      }
    }
  }
  &-logo {
    flex: 1;
    img {
      height: 46px;
    }
    @media (max-width: 1400px) {
      text-align: center;
      margin: 16px 0;
      .show-pc {
        display: none;
      }
      .show-mo {
        display: inline-block;
        height: 20px;
      }
    }
  }

  .copy-right {
    font-size: var(--o-font-size-text);
    color: #fff;
    margin-top: var(--o-spacing-h5);
    @media (max-width: 1400px) {
      font-size: var(--o-font-size-tip);
      line-height: var(--o-line-height-tip);
      margin-top: var(--o-spacing-h8);
    }
  }
  .license {
    font-size: var(--o-font-size-text);
    color: #fff;
    margin-top: var(--o-spacing-h5);
    span {
      color: var(--o-color-text-secondary);
    }
    @media (max-width: 1400px) {
      font-size: var(--o-font-size-tip);
      line-height: var(--o-line-height-tip);
      margin-top: var(--o-spacing-h8);
    }
  }

  .footer-option {
    text-align: center;
    .link {
      color: #fff;
      font-size: var(--o-font-size-text);
      display: inline-block;
      padding: 0 var(--o-spacing-h6);
      border-right: 1px solid #fff;
      text-decoration: none;
      &:last-child {
        border-right: 0;
      }
      @media (max-width: 1400px) {
        font-size: var(--o-font-size-tip);
        line-height: var(--o-line-height-tip);
        padding: 0 var(--o-spacing-h9);
      }
    }
    @media (max-width: 1400px) {
      order: -1;
    }
  }
  .footer-right {
    flex: 1;
    .code-box {
      display: flex;
      justify-content: right;
      gap: 16px;
      margin-bottom: 16px;
      .code-pop {
        position: relative;
        height: 20px;
        display: block;
        > img {
          height: 100%;
          object-fit: cover;
        }
        .code-layer {
          position: absolute;
          top: -105px;
          left: -32px;
          z-index: 99;
          display: none;
          background: #fff;
          padding: 6px;
          img {
            width: 78px;
            height: 78px;
          }
          .txt {
            font-size: 12px;
            color: #fff;
            display: none;
          }
          &::after {
            border: 10px solid transparent;
            content: '';
            border-top-color: #fff;
            position: absolute;
            bottom: -20px;
            left: 50%;
            transform: translateX(-50%);
            display: block;
          }
          @media (max-width: 800px) {
            display: block;
            position: initial;
            background: none;
            padding: 0;
            text-align: center;
            &::after {
              display: none !important;
            }
            .txt {
              display: block;
            }
          }
        }
        &:hover {
          .code-layer {
            display: block;
          }
        }
        @media (max-width: 800px) {
          height: auto;
          > img {
            display: none;
          }
        }
      }
      @media (max-width: 1400px) {
        justify-content: center;
      }
      @media (max-width: 1100px) {
        margin-top: 24px;
      }
    }
    .footer-links {
      display: flex;
      justify-content: right;
      align-items: center;
      gap: 16px;
      .links-logo {
        height: 16px;
        img {
          height: 100%;
          object-fit: cover;
        }
      }
      @media (max-width: 1100px) {
        justify-content: center;
      }
      @media (max-width: 800px) {
        display: flex;
        text-align: center;
        .img {
          height: 16px;
        }
      }
    }

    p {
      color: #fff;
      font-size: var(--o-font-size-tip);
      margin-top: var(--o-spacing-h8);
    }
  }

  .email {
    display: block;
    margin-top: 4px;
    color: #fff;
    font-size: var(--o-font-size-text);
    @media (max-width: 1400px) {
      font-size: var(--o-font-size-tip);
    }
  }
  .float-right {
    position: fixed;
    display: flex;
    flex-direction: column;
    top: 70vh;
    right: 50px;
    z-index: 10;
    box-shadow: var(--o-shadow-l1);
    .nav-item {
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      width: 50px;
      height: 50px;
      background-color: var(--o-color-bg2);
      background-size: cover;
      font-size: 12px;
      line-height: 18px;
      color: var(--o-color-text1);
      .text {
        word-spacing: 100vw;
        display: none;
      }
      .o-icon {
        font-size: 24px;
      }
      &:hover {
        color: var(--o-color-white);
        background-color: var(--o-color-black);
        .o-icon {
          display: none;
        }
        .text {
          display: block;
        }
      }
    }

    @media screen and (max-width: 1200px) {
      display: none;
    }
  }
  .float-left {
    left: 40px;
    right: inherit;
    box-shadow: none;
    .close {
      cursor: pointer;
      position: absolute;
      width: 25px;
      height: 25px;
      top: 0;
      right: 0;
      z-index: 11;
    }
    img {
      width: 150px;
    }
  }
}
</style>
