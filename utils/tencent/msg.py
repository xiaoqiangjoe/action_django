from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models


def send_message(phone, random_code):
    '''
    下面的配置最好写在settings里
    :param phone:
    :param random_code:
    :return:
    '''
    try:
        phone = '{}{}'.format("+86",phone)
        cred = credential.Credential("AKIDkGlz4tb2i8GAqSosgHdiZElHafX9bbPI", "nKtDmsncS4QVUEispiNmvue8QSO5WhiU")
        client = sms_client.SmsClient(cred, "ap-beijing")
        req = models.SendSmsRequest()

        # 短信应用ID: 短信SdkAppid在 [短信控制台] 添加应用后生成的实际SdkAppid，示例如1400006666
        req.SmsSdkAppid = "1400320908"
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，签名信息可登录 [短信控制台] 查看
        req.Sign = "乔晓强个人公众号"
        # 下发手机号码，采用 e.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = [phone,]
        # 模板 ID: 必须填写已审核通过的模板 ID。模板ID可登录 [短信控制台] 查看
        req.TemplateID = "541725"
        # 模板参数: 若无模板参数，则设置为空
        req.TemplateParamSet = [random_code,]

        # 通过client对象调用DescribeInstances方法发起请求。注意请求方法名与请求对象是对应的。
        # 返回的resp是一个DescribeInstancesResponse类的实例，与请求对象对应。
        resp = client.SendSms(req)

        # 输出json格式的字符串回包
        if resp.SendStatusSet[0].Code == 'Ok':
            return True
        # print(resp.to_json_string(indent=2))

    except TencentCloudSDKException as err:
        # print(err)
        pass