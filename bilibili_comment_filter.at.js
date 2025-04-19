// ==UserScript==
// @name         B站评论过滤器 - 过滤@用户评论
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  过滤掉B站评论区中包含@用户的评论
// @author       Misasasasasaka
// @match        *://*.bilibili.com/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    // 是否包含@用户
    function hasAtUser(message) {
        if (!message || typeof message !== 'string') return false;
        return message.includes('@');
    }

    // 过滤主评论列表
    function filterReplies(replies) {
        if (!replies || !Array.isArray(replies)) return replies;

        return replies.filter(reply => {
            if (!reply || !reply.content) return true;
            return !hasAtUser(reply.content.message);
        });
    }

    // 处理对象中的评论数据
    function processCommentData(data) {
        if (!data) return data;

        // 处理主评论列表
        if (data.replies) {
            data.replies = filterReplies(data.replies);
        }

        // 处理热评列表
        if (data.hots) {
            data.hots = filterReplies(data.hots);
        }

        // 处理回复列表
        if (data.root && data.root.replies) {
            data.root.replies = filterReplies(data.root.replies);
        }

        return data;
    }

    // 拦截XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function() {
        this._url = arguments[1];
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        if (this._url && (
            this._url.includes('/x/v2/reply') ||
            this._url.includes('/x/v2/reply/wbi/main') ||
            this._url.includes('/x/v2/reply/reply') ||
            this._url.includes('/x/v2/reply/dialog/cursor')
        )) {
            const originalOnReadyStateChange = this.onreadystatechange;
            this.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200) {
                    try {
                        const response = JSON.parse(this.responseText);
                        if (response.data) {
                            response.data = processCommentData(response.data);
                            Object.defineProperty(this, 'responseText', {
                                writable: true,
                                value: JSON.stringify(response)
                            });
                        }
                    } catch (e) {
                        console.error('B站评论过滤器处理评论数据出错:', e);
                    }
                }
                if (originalOnReadyStateChange) {
                    originalOnReadyStateChange.apply(this, arguments);
                }
            };
        }
        return originalXHRSend.apply(this, arguments);
    };

    // 拦截Fetch API
    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        const url = typeof input === 'string' ? input : input.url;

        if (url && (
            url.includes('/x/v2/reply') ||
            url.includes('/x/v2/reply/wbi/main') ||
            url.includes('/x/v2/reply/reply') ||
            url.includes('/x/v2/reply/dialog/cursor')
        )) {
            return originalFetch.apply(this, arguments)
                .then(response => {
                    const clonedResponse = response.clone();
                    return clonedResponse.json()
                        .then(data => {
                            if (data.data) {
                                data.data = processCommentData(data.data);
                                const modifiedResponse = new Response(JSON.stringify(data), {
                                    status: response.status,
                                    statusText: response.statusText,
                                    headers: response.headers
                                });
                                return modifiedResponse;
                            }
                            return response;
                        })
                        .catch(() => response);
                });
        }

        return originalFetch.apply(this, arguments);
    };

    console.log("B站评论过滤器已启用 - 过滤@用户评论");
})();
