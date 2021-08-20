# MyApi

## DouyinApi

功能：直接粘贴分享链接即可识别链接的类型进行下载。

无水印下载单个视频和相册，下载单个用户所有作品或者喜欢（改一下就行），支持合集下载，对文件名校验。

实现了话题分享下载视频。对于signature，不能用于搜索的接口。Fuck Douyin!!!!!!!!!!!!!

实现了短剧下载。

太菜了，好几个类写法都差不多，有空改进一下。音乐合集下载不想写了估计是一样的。

DouyinApi就到此结束吧，就当作练练手了。

没有实现的，音乐合集下载。

### API参考：

------

视频和相册接口：

视频id不用多说，相册id从手机分享的url中来。返回json格式数据，其中`aweme_type`代表视频还是相册。在获得的下载链接中如果有`/playwm/`，这是有水印的，改为`/play/`。

```
https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={视频或者相册id}
```

用户页接口：

小姐姐测试：https://www.douyin.com/user/MS4wLjABAAAAlKSDDV19aih7W6POOHk9bh4vbkHl00HCST4hgou7beM?previous_page=app_code_link

![userApi](https://raw.githubusercontent.com/orzchen/MyApi/master/doc/imgs/userApi.gif)

用户作品列表api，用户secid可从url，或手机分享的url访问查看。请求中`_signature`可以在代码中打开自动生成，也可以一直用一个。`count`和`max_cursor`关系：`max_cusor`从`0`开始代表第一页，返回的数据中`max_cursor`是下一页的。最后一页的`max_cursor`接着访问得到的是空`aweme_list`。

```
https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={用户SecID}&count={每页数目}&max_cursor={页码}&aid=1128&_signature={signature}
```

合集接口：

合集列表api和合集信息api，合集id可从url，或手机分享的url访问查看。`count`和`cursor`关系：`cusor`从`0`开始代表第一页，返回的数据中`cursor`是下一页的，最后一页的`cousor`不变。

```
https://www.iesdouyin.com/web/api/mix/item/list/?mix_id={合集id}&count={每页数目}&cursor={页码}
https://www.iesdouyin.com/web/api/mix/detail/?mix_id={合集id}
```

话题接口：

话题作品列表api和话题信息api，话题id可从url，或手机分享的url访问查看。请求中`_signature`可以在代码中打开自动生成，也可以一直用一个。`count`和`cursor`关系：`cusor`从`0`开始代表第一页，返回的数据中`cursor`是本页的，不是下一页的，下一页的`cursor`是加上`count`的值。

```
https://www.iesdouyin.com/web/api/v2/challenge/aweme/?ch_id={话题id}&count={每页数目}&cursor={页码}&aid=1128&screen_Limit=3&download_click_limit=0&_signature={signature}
https://www.iesdouyin.com/web/api/v2/challenge/info/?ch_id={话题id}
```

短剧接口：

短剧作品列表api和短剧信息api，短剧id可从url，或手机分享的url访问查看。`count`和`cursor`关系：`cusor`从`0`开始代表第一页，返回的数据中`cursor`是下一页的，最后一页的`cousor`不变。

```
https://www.iesdouyin.com/web/api/playlet/item/list/?playlet_id={短剧id}&count={每页数目}&cursor={页码}
https://www.iesdouyin.com/web/api/playlet/detail/?playlet_id={短剧id}
```

热榜接口：

```
https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/
```

搜索接口：

```
https://www.douyin.com/aweme/v1/web/search/item/?device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_video_web&sort_type=0&publish_time=0&keyword={关键字}&search_source=normal_search&query_correct_type=1&is_filter_search=0&offset=0&count=30&version_code=160100&version_name=16.1.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows)&browser_online=true&_signature={去他妈的_signature}
```

其他花里胡哨的接口：[douyin_web_signature](https://github.com/coder-fly/douyin_web_signature)