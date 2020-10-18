# 第十二天


## 环境管理

1.  添加model类
在models.py中添加
```
class Env(BaseTable):
    class Meta:
        verbose_name = '环境管理'
        db_table = 'EnvInfo'

    env_name = models.CharField(max_length=40, null=False, unique=True)
    base_url = models.CharField(max_length=40, null=False)
    simple_desc = models.CharField(max_length=50, null=False)
    objects = EnvManager()
```
导入 EvnManager
在models.py中将`from .managers import TestConfigManager`改为
`from .managers import TestConfigManager, EnvManager,`

2.  managers.py 添加EnvManager类
```
class EnvManager(models.Manager):
    def insert_env(self, **kwargs):
        self.create(**kwargs)

    def update_env(self, index, **kwargs):
        obj = self.get(id=index)
        obj.env_name = kwargs.pop('env_name')
        obj.base_url = kwargs.pop('base_url')
        obj.simple_desc = kwargs.pop('simple_desc')
        obj.save()

    def get_env_name(self, index):
        return self.get(id=index).env_name

    def delete_env(self, index):
        self.get(id=index).delete()
```
3.  添加视图

```
def env_list(request):
    if request.method == "GET":
        env_name = request.GET.get('env_name','')
        info = {'env_name': env_name}
        if env_name:
            rs = Env.objects.filter(env_name=env_name).order_by("-update_time")
        else:
            rs = Env.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'env': objects, 'info': info }
        return render(request,"env_list.html",context_dict)

@csrf_exempt
def env_set(request):
    """
    环境设置
    :param request:
    :return:
    """

    if request.is_ajax():
        env_lists = json.loads(request.body.decode('utf-8'))
        msg = env_data_logic(**env_lists)
        if msg == 'ok':
            return HttpResponse(reverse('env_list'))
        else:
            return HttpResponse(msg)
        
    elif request.method == 'GET':
        return render(request, 'env_list.html')
```
在utils.py中添加evn_data_logic函数
[utils.py](./Chapter-12-code/hat/httpapitest/utils.py)
在utils.py中导入Env
将`from .models import TestConfig, Module`改为
`from .models import TestConfig, Module, Env`

在views.py中导入`env_data_logic`
将`from .utils import config_logic` 改为
`from .utils import config_logic, env_data_logic,`

在views.py中导入Env 类
将`from httpapitest.models import Project, DebugTalk, Module, TestConfig`改为
`from httpapitest.models import Project, DebugTalk, Module, TestConfig, Env`

4. 添加模板 env_list.html
[env_list.html](./Chapter-12-code/hat/templates/env_list.html)

5. 添加url
```
path('env/list', views.env_list, name='env_list'),
path('env/set', views.env_set, name='env_set'),
```

## 用例管理
测试用例的增删改查

###  添加model 类TestCase

添加Testcase类的 管理类 
在managers.py 添加 TestCaseManager 类

[managers.py](./Chapter-12-code/hat/httpapitest/managers.py)


```
class TestCase(BaseTable):
    class Meta:
        verbose_name = '用例信息'
        db_table = 'TestCaseInfo'
    name = models.CharField('用例名称', max_length=50, null=False)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    belong_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    include = models.CharField('前置config/test', max_length=1024, null=True)
    author = models.CharField('创建者', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)
    objects = TestCaseManager()
```
导入 TestCaseManager 类
修改`from .managers import TestConfigManager, EnvManager`为
`from .managers import TestConfigManager, EnvManager, TestCaseManager`
执行数据库迁移命令

###  添加用例

1. 添加视图函数 

```
@csrf_exempt
def case_add(request):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(request, 'case_add.html', context_dict)
    if request.is_ajax():
        testcase = json.loads(request.body.decode('utf-8'))
        msg = case_logic(**testcase)
        if msg == 'ok':
            return HttpResponse(reverse('case_list'))
        else:
            return HttpResponse(msg)


@csrf_exempt
def case_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
            module = data["case"]["name"]["module"]
        if   project != "请选择" and module != "请选择":
            m = Module.objects.get(id=module)
            cases = TestCase.objects.filter(belong_project=project, belong_module=m)
            case_list = ['%d^=%s' % (c.id, c.name) for c in cases ]
            case_string = 'replaceFlag'.join(case_list)
            return HttpResponse(case_string)
        else:
            return HttpResponse('')

@csrf_exempt
def config_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
            module = data["case"]["name"]["module"]
        if   project != "请选择" and module != "请选择":
            m = Module.objects.get(id=module)
            configs = TestConfig.objects.filter(belong_project=project, belong_module=m)
            config_list = ['%d^=%s' % (c.id, c.name) for c in configs ]
            config_string = 'replaceFlag'.join(config_list)
            return HttpResponse(config_string)
        else:
            return HttpResponse('')

def case_list(request):
    pass


def case_edit(request):
    pass

def case_delete(request):
    pass

def case_copy(request):
    pass


```
导入函数case_logic
在views.py中修改`from .utils import config_logic, env_data_logic` 为
`from .utils import config_logic, env_data_logic, case_logic`
导入TestCase
`from httpapitest.models import Project, DebugTalk, Module, TestConfig, Env`为
`from httpapitest.models import Project, DebugTalk, Module, TestConfig, Env, TestCase`


2. 添加视图函数所调用的的函数
在utils.py 中添加case_logic， add_case_data, update_include函数

[utils.py](./Chapter-12-code/hat/httpapitest/utils.py)

在utils.py中导入TestCase
修改`from .models import TestConfig, Module, Env`为
`from .models import TestConfig, Module, Env, TestCase`


4. 添加模板文件 case_add.html

[case_add.html](./Chapter-12-code/hat/templates/case_add.html)

5. 添加模板case_add.html 所使用的过滤器conver_eval, id_del

templatetags/custom_tags.py添加自定义过滤器 convert_eval,id_del
[custom_tags.py](./Chapter-12-code/hat/httpapitest/templatetags/custom_tags.py)
并导入函数`from httpapitest.utils import update_include`

6. 在commons.js 中添加case_add.html 中使用的js 函数 case_ajax
在commons.js中添加函数case_ajax

[commons.js](./Chapter-12-code/hat/static/assets/js/commons.js)

在urls.py 中添加
```
    path('case/add', views.case_add, name='case_add'),
    path('case/search/ajax', views.case_search_ajax, name='case_search_ajax'),
    path('config/search/ajax', views.config_search_ajax, name='config_search_ajax'),
    path('case/edit/<int:id>', views.case_edit, name='case_edit'),
    path('case/list', views.case_list, name='case_list'),
    path('case/delete', views.case_delete, name='case_delete'),
    path('case/copy', views.case_copy, name='case_copy'),
    
```


###  用例列表 

更新case_list 视图

```
@csrf_exempt
def case_list(request):
    if request.method == 'GET':
        env = Env.objects.all()
        projects = Project.objects.all().order_by("-update_time")

        project = request.GET.get('project','All')
        module = request.GET.get('module', "请选择")
        name = request.GET.get('name','')
        user = request.GET.get('user','')
        
        if project == "All":
            if name:
                rs = TestCase.objects.filter(name=name)
            elif user:
                rs = TestCase.objects.filter(author=user).order_by("-update_time")
            else:
                rs = TestCase.objects.all().order_by("-update_time")
        else:
            if module != "请选择":
                m = Module.objects.get(id=module)
                if name:
                    rs = TestCase.objects.filter(belong_module=m, belong_project=project, name=name)
                elif user:
                    rs = TestCase.objects.filter(belong_project=project,author=user).order_by("-update_time")
                else:
                    rs = TestCase.objects.filter(belong_module=m, belong_project=project).order_by("-update_time")
                module = m
                logger.info(module)
                
            else:
                if name:
                    rs = TestCase.objects.filter(belong_project=project, name=name)
                elif user:
                    rs = TestCase.objects.filter(belong_project=project, author=user).order_by("-update_time")
                else:
                    rs = TestCase.objects.filter(belong_project=project).order_by("-update_time")
        info = {'belong_project': project, 'belong_module': module, 'name': name, 'user':user}        
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'case': objects, 'projects': projects, 'info':info}
        return render(request,"case_list.html",context_dict)
```


添加模板case_list.html
[case_list.html](./Chapter-12-code/hat/templates/case_list.html)

添加依赖的url和视图
```
# 在urls.py中添加以下内容
path('test/test_run', views.test_run, name='test_run'),
path('test/test_batch_run', views.test_batch_run, name='test_batch_run'),

# 在views.py中添加以下内容
def test_run(request):
    pass

def test_batch_run(request):
    pass
```
在commons.js中添加函数
```
function post(url, params) {
    var temp = document.createElement("form");
    temp.action = url;
    temp.method = "post";
    temp.style.display = "none";
    for (var x in params) {
        var opt = document.createElement("input");
        opt.name = x;
        opt.value = params[x];
        temp.appendChild(opt);
    }
    document.body.appendChild(temp);
    temp.submit();
    return temp;
}
```

###  编辑功能

1. 更新case_edit 视图
```
@csrf_exempt
def case_edit(request, id):
    if request.method == 'GET':
        case = TestCase.objects.get(id=id)
        case_request = eval(case.request)
        case_include = eval(case.include)
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time'),
            'info': case,
            'request': case_request['test'],
            'include': case_include
        }
        return render(request, 'case_edit.html', context_dict)

    if request.is_ajax():
        case_list = json.loads(request.body.decode('utf-8'))
        msg = case_logic(type=False, **case_list)
        if msg == 'ok':
            return HttpResponse(reverse('case_list'))
        else:
            return HttpResponse(msg)
```

2. 添加case_edit.html模板

[case_edit.html](./Chapter-12-code/hat/templates/case_edit.html)
测试编辑功能

###  删除功能
修改case_delete视图
```
@csrf_exempt
def case_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        case_id = data.get('id')
        case = TestCase.objects.get(id=case_id)
        case.delete()
        return HttpResponse(reverse('case_list'))
```

测试删除功能

###  拷贝功能
```
@csrf_exempt
def case_copy(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data['data']['index']
        name = data['data']['name']
        case = TestCase.objects.get(id=config_id)
        belong_module = case.belong_module
        if TestCase.objects.filter(name=name, belong_module=belong_module).count() > 0:
            return HttpResponse("用例名称重复")
        else:
            case.name = name
            case.id = None
            case.save()
            return HttpResponse(reverse('case_list'))
```

测试拷贝功能

## 用例运行
执行测试用例

1. 添加视图函数test_run
```
@csrf_exempt
def test_run(request):
    """
    运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        id = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        run_test_by_type(id, base_url, testcase_dir_path, type)
        report_name = kwargs.get('report_name', None)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        id = request.POST.get('id')
        base_url = request.POST.get('env_name')
        type = request.POST.get('type', 'test')

        run_test_by_type(id, base_url, testcase_dir_path, type)
        runner.run(testcase_dir_path)
        #shutil.rmtree(testcase_dir_path)
        summary = timestamp_to_datetime(runner._summary, type=False)
        print(summary)

        return render(request,'report_template.html', summary)

```

2. views.py 导入函数
```
from .utils import  get_time_stamp,timestamp_to_datetime
from httprunner.api import HttpRunner
from .runner import run_test_by_type,run_by_single
import logging
import os,shutil
```
3. 创建要导入的函数
在utils.py 文件中添加dump_yaml_file，dump_python_file，get_time_stamp，timestamp_to_datetime
并导入
`import time,io,yaml,datetime`

[utils.py](./Chapter-12-code/hat/httpapitest/utils.py)

在httpapitest添加runner.py文件
用例使用的是run_test_by_type,run_by_single，其它函数在批量运行时使用

[runner.py](./Chapter-12-code/hat/httpapitest/runner.py)

4. 添加模板文件

[report_template.html](./Chapter-12-code/hat/templates/report_template.html)



测试用例运行


## 批量运行

### 用例批量运行
1. 添加批量运行视图
```
@csrf_exempt
def test_batch_run(request):
    """
    批量运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        test_list = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        report_name = kwargs.get('report_name', None)
        run_by_batch(test_list, base_url, testcase_dir_path, type=type)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        type = request.POST.get('type', None)
        base_url = request.POST.get('env_name')
        test_list = request.body.decode('utf-8').split('&')
        if type:
            run_by_batch(test_list, base_url, testcase_dir_path, type=type, mode=True)
        else:
            run_by_batch(test_list, base_url, testcase_dir_path)

        runner.run(testcase_dir_path)

        shutil.rmtree(testcase_dir_path)
        summary = timestamp_to_datetime(runner._summary, type=False)
        print(summary)
        return render(request,'report_template.html', summary)
```


### 测试用例批量运行
在views.py中导入
`from .runner import run_test_by_type,run_by_single,run_by_batch`

### 模块批量运行功能
修改module_list.html模板,找到运行按钮添加onclick属性，并在js部分添加下面js代码
添加
[module_list.html](./Chapter-12-code/hat/templates/module_list.html)

两个运行button
```
                <button type="button" class="am-btn am-btn-danger am-round am-btn-xs am-icon-bug"
                         onclick="run_test('batch','{% url 'test_batch_run' %}', 'module')">运行
                </button>


                                    <button type="button"
                                            class="am-btn am-btn-default am-btn-xs am-text-secondary am-round"
                                            data-am-popover="{content: '运行', trigger: 'hover focus'}"
                                            onclick="run_test('{{ foo.id }}', '{% url 'test_run' %}', 'module')"
                                            >
                                        <span class="am-icon-bug"></span>
                                    </button>


```

script 部分                                
```     
        function run_test(mode,url, type) {
            if (mode === 'batch') {
                if ($("input:checked").size() === 0) {
                    myAlert("请至少选择一个模块运行！");
                    return;
                }
            }
            $('#select_env').modal({
                relatedTarget: this,
                onConfirm: function () {
                    var data = {
                        "id": $("#module_list").serializeJSON(),
                        "env_name": $('#env_name').val(),
                        "type": type,
                        'report_name': $('#report_name').val()
                    };
                    if (mode !== 'batch') {
                        data["id"] = mode;
                    }
                    if ($('#mode').val() === 'true') {
                        if (mode === 'batch') {
                            var json2map = JSON.stringify(data['id']);
                            var obj = JSON.parse(json2map);
                            obj['env_name'] = data['env_name'];
                            obj['type'] = data['type'];
                            post('{% url 'test_batch_run' %}', obj);
                        } else {
                            post('{% url 'test_run' %}', data);
                        }
                    } else {
                        $.ajax({
                            type: 'post',
                            url: url,
                            data: JSON.stringify(data),
                            contentType: "application/json",
                            success: function (data) {
                                myAlert(data);
                            },
                            error: function () {
                                myAlert('Sorry，服务器可能开小差啦, 请重试!');
                            }
                        });
                    }
                },
                onCancel: function () {
                }
            });
        }
```
添加id='select_env' 的modal
```
    <div class="am-modal am-modal-confirm" tabindex="-1" id="select_env">
        <div class="am-modal-dialog">
            <div class="am-modal-hd">HAT</div>
            <form class="form-horizontal">
                <div class="form-group">
                    <label class="control-label col-sm-3"
                           style="font-weight: inherit; font-size: small ">运行环境:</label>
                    <div class="col-sm-8">
                        <select class="form-control" id="env_name" name="env_name">
                            <option value="">自带环境</option>
                            {% for foo in env %}
                                <option value="{{ foo.base_url }}">{{ foo.env_name }}</option>
                            {% endfor %}

                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="control-label col-sm-3" for="report_name"
                           style="font-weight: inherit; font-size: small ">报告名称：</label>
                    <div class="col-sm-8">
                        <input name="report_name" type="text" id="report_name" class="form-control"
                               placeholder="默认时间戳命名" value="" readonly>
                    </div>
                </div>

                <div class="form-group">
                    <label class="control-label col-sm-3"
                           style="font-weight: inherit; font-size: small ">执行方式:</label>
                    <div class="col-sm-8">
                        <select class="form-control" id="mode" name="mode">
                            <option value="true">同步(执行完立即返回报告)</option>
                            <option value="false">异步(后台执行，完毕后可查看报告)</option>
                        </select>
                    </div>
                </div>
            </form>
            </form>

            <div class="am-modal-footer">
                <span class="am-modal-btn" data-am-modal-cancel>取消</span>
                <span class="am-modal-btn" data-am-modal-confirm>确定</span>
            </div>
        </div>
    </div>

```

测试模块运行

### 项目批量运行
修改project_list.html模板,找到运行按钮添加onclick属性，并在js部分添加下面js代码
[module_list.html](./Chapter-12-code/hat/templates/project_list.html)
修改同module_list.html



## celery

Celery 是一个简单、灵活且可靠的，处理大量消息的分布式系统，并且提供维护这样一个系统的必需工具。是一个专注于实时处理的任务队列，同时也支持任务调度。


任务队列用作跨线程或机器分配工作的机制。 任务队列的输入是为一个任务。任务队列通过消息系统borker实现。客户端往broker中加任务，worker进程不断监视broker中的任务队列以执行新的任务


支持的常见broker
+ redis
+ rabbitmq
+ zookeeper

安装支持redis的celery
```
pip install celery -i https://pypi.douban.com/simple/
pip install redis -i https://pypi.douban.com/simple/
pip install  eventlet -i https://pypi.douban.com/simple/
```


编写tasks.py
```
from celery import Celery

app = Celery('tasks', broker='redis://127.0.0.1:6379/0')

@app.task
def add(x, y):
    return x + y
```


client.py
```
from tasks import add
add.delay(2,3) 
```

启动 redis
执行client.py 生成一个要执行的任务
`python client.py`
查看redis key
```
127.0.0.1:6379> keys *
1) "celery"
2) "_kombu.binding.celery"
```
查看key类型
```
127.0.0.1:6379> type celery
list
127.0.0.1:6379> type "_kombu.binding.celery"
set
```
查看key 的value
```
127.0.0.1:6379> lrange celery 0 -1
1) "{\"body\": \"W1syLCAzXSwge30sIHsiY2FsbGJhY2tzIjogbnVsbCwgImVycmJhY2tzIjogbnVsbCwgImNoYWluIjogbnVsbCwgImNob3JkIjogbnVsbH1d\", \"content-encoding\": \"utf-8\", \"content-type\": \"application/json\", \"headers\": {\"lang\": \"py\", \"task\": \"tasks.add\", \"id\": \"d0ac9482-bb5f-4b4d-8b70-625cd88aad0d\", \"shadow\": null, \"eta\": null, \"expires\": null, \"group\": null, \"retries\": 0, \"timelimit\": [null, null], \"root_id\": \"d0ac9482-bb5f-4b4d-8b70-625cd88aad0d\", \"parent_id\": null, \"argsrepr\": \"(2, 3)\", \"kwargsrepr\": \"{}\", \"origin\": \"gen15684@LAPTOP-PHMJ1QN6\"}, \"properties\": {\"correlation_id\": \"d0ac9482-bb5f-4b4d-8b70-625cd88aad0d\", \"reply_to\": \"7d107092-94b4-35c8-bb26-20063dc7944d\", \"delivery_mode\": 2, \"delivery_info\": {\"exchange\": \"\", \"routing_key\": \"celery\"}, \"priority\": 0, \"body_encoding\": \"base64\", \"delivery_tag\": \"3526616e-1efc-4eae-867d-1715c8751531\"}}"

127.0.0.1:6379> smembers "_kombu.binding.celery"
1) "celery\x06\x16\x06\x16celery"
```


celery 为一个任务队列列表 等待执行的任务都在这个列表里
_kombu.binding.celery 默认的任务队列名称默认为 celery



启动worker

`celery -A tasks worker --loglevel=info  -P eventlet`







