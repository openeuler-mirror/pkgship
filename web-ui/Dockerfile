FROM node:16.13.1-alpine as Builder

MAINTAINER zhangxiaopan<zhangxiaopan2@huawei.com>

RUN mkdir -p /home/openeuler/pkgwebui
WORKDIR /home/openeuler/pkgwebui
COPY . /home/openeuler/pkgwebui

RUN npm install -g vue && \
    npm install && \
    npm run build

FROM swr.cn-north-4.myhuaweicloud.com/opensourceway/openeuler/nginx:1.22.0-22.03-lts

COPY --from=Builder /home/openeuler/pkgwebui/dist /usr/share/nginx/html/
RUN chmod -R 755 /usr/share/nginx/html
RUN rm -rf  /usr/share/nginx/html/ru
COPY ./deploy/nginx/nginx.conf /etc/nginx/nginx.conf

RUN touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /var/run/nginx.pid \
    && chown -R nginx:nginx /etc/nginx
EXPOSE 8080
USER nginx
ENTRYPOINT ["nginx", "-g", "daemon off;"]


