<template>
    <div id="app" v-cloak>
        <i-header></i-header>
        <div class="content">
            <router-view />
        </div>
        <i-footer></i-footer>
    </div>
</template>

<script>
import header from "_c/header";
import footer from "_c/footer";
export default {
    data() {
        return {};
    },
    components: {
        "i-header": header,
        "i-footer": footer
    }
};
</script>

<style lang="less" scoped>
[v-cloak] {
    display: none !important;
}
.content {
    min-height: calc(100vh - 60px - 226px);
    @media (max-width: 1000px) {
        min-height: calc(100vh - 70px - 280px);
    }
}
</style>
