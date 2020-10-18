from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from httpapitest.models import Project, DebugTalk, Module, TestConfig, Env, TestCase
from django.shortcuts import reverse, redirect
from django.core.paginator import Paginator
from .utils import config_logic, env_data_logic, case_logic
from .utils import  get_time_stamp,timestamp_to_datetime
from httprunner.api import HttpRunner
from .runner import run_test_by_type,run_by_single,run_by_batch
import logging
import os,shutil

# Create your views here.
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def project_add(request):
    if request.is_ajax():
        project = json.loads(request.body.decode('utf-8'))
        if project.get('project_name') == '':
            msg = '项目名称不能为空'
            return HttpResponse(msg)
        if project.get('responsible_name') == '':
            msg = '负责人不能为空'
            return HttpResponse(msg)
        if project.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        if project.get('dev_user') == '':
            msg = '开发人员不能为空'
            return HttpResponse(msg)
        if project.get('publish_app') == '':
            msg = '发布应用不能为空'
            return HttpResponse(msg)
        if Project.objects.filter(project_name=project.get('project_name')):
            msg = "项目已经存在"
            return HttpResponse(msg)
        else:
            p = Project()
            p.project_name = project.get('project_name')
            p.responsible_name = project.get('responsible_name')
            p.test_user = project.get('test_user')
            p.dev_user = project.get('dev_user')
            p.publish_app = project.get('publish_app')
            p.simple_desc = project.get('simple_desc')
            p.other_desc = project.get('other_desc')
            p.save()
            d = DebugTalk()
            d.belong_project = p
            d.save()
            return HttpResponse(reverse('project_list'))
       

    if request.method == 'GET':
        return render(request, 'project_add.html')

@csrf_exempt
def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by("-update_time")
        project_name = request.GET.get('project','All')

        user = request.GET.get('user', '负责人')
        info = {'belong_project': project_name, 'user':user}

        
        if project_name != "All":
            rs = Project.objects.filter(project_name=project_name)
        elif user != "负责人":
            rs = Project.objects.filter(responsible_name=user)
        else:
            rs = projects
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'project': objects, 'all_projects': projects,'info': info}
        return render(request,"project_list.html",context_dict)

@csrf_exempt
def project_edit(request):
    if request.is_ajax():
        project = json.loads(request.body.decode('utf-8'))
        if project.get('project_name') == '':
            msg = '项目名称不能为空'
            return HttpResponse(msg)
        if project.get('responsible_name') == '':
            msg = '负责人不能为空'
            return HttpResponse(msg)
        if project.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        if project.get('dev_user') == '':
            msg = '开发人员不能为空'
            return HttpResponse(msg)
        if project.get('publish_app') == '':
            msg = '发布应用不能为空'
            return HttpResponse(msg)
        else:
            p = Project.objects.get(project_name=project.get('project_name'))
            p.responsible_name = project.get('responsible_name')
            p.test_user = project.get('test_user')
            p.dev_user = project.get('dev_user')
            p.publish_app = project.get('publish_app')
            p.simple_desc = project.get('simple_desc')
            p.other_desc = project.get('other_desc')
            p.save()
            return HttpResponse(reverse('project_list'))
        

@csrf_exempt
def project_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        project_id = data.get('id')
        project = Project.objects.get(id=project_id)
        project.delete()
        return HttpResponse(reverse('project_list'))

@csrf_exempt
def module_add(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by("-update_time")
        context_dict = {'data': projects}
        return render(request, 'module_add.html',context_dict)
    if request.is_ajax():
        module = json.loads(request.body.decode('utf-8'))
        if module.get('module_name') == '':
            msg = '模块名称不能为空'
            return HttpResponse(msg)
        if module.get('belong_project') == '请选择':
            msg = '请选择项目，没有请先添加哦'
            return HttpResponse(msg)
        if module.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        p = Project.objects.get(project_name=module.get('belong_project'))
        if Module.objects.filter(module_name=module.get('module_name'), belong_project=p):
            msg = "项目已经存在"
            return HttpResponse(msg)
        else:
            m = Module()
            m.module_name = module.get('module_name')
            p = Project.objects.get(project_name=module.get('belong_project'))
            m.belong_project = p
            m.test_user = module.get('test_user')
            m.simple_desc = module.get('simple_desc')
            m.other_desc = module.get('other_desc')
            m.save()
            return HttpResponse(reverse('module_list'))
        

@csrf_exempt
def module_list(request):
    if request.method == 'GET':
        
        projects = Project.objects.all().order_by("-update_time")
        project = request.GET.get("project", "All")
        module = request.GET.get("module", "请选择")
        user = request.GET.get("user", '')
        

        if project == "All":
            if user:
                rs = Module.objects.filter(test_user=user).order_by("-update_time")
               
            else:
                rs = Module.objects.all().order_by("-update_time")
        else:
            p = Project.objects.get(project_name=project)
            if module != "请选择":
                if user:
                    rs = Module.objects.filter(id=module, belong_project=p, test_user=user).order_by("-update_time")
                else:
                    rs = Module.objects.filter(id=module, belong_project=p).order_by("-update_time")
                module = Module.objects.get(id=module)
            else:
                if user:
                    rs = Module.objects.filter(belong_project=p, test_user=user).order_by("-update_time")
                else:
                    rs = Module.objects.filter(belong_project=p).order_by("-update_time")
        info = {'belong_project': project,'belong_module': module, 'user':user}
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'module': objects, 'projects': projects, 'info': info }
        return render(request,"module_list.html",context_dict)

@csrf_exempt
def module_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'test' in data.keys():
            project = data["test"]["name"]["project"]
        if 'config' in data.keys():
            project = data["config"]["name"]["project"]
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
        if 'upload' in data.keys():
            project = data["upload"]["name"]["project"]
        if 'crontab' in data.keys():
            project = data["crontab"]["name"]["project"]
        if  project != "All" and project != "请选择":
            p = Project.objects.get(project_name=project)
            modules = Module.objects.filter(belong_project=p)
            modules_list = ['%d^=%s' % (m.id, m.module_name) for m in modules ]
            modules_string = 'replaceFlag'.join(modules_list)
            return HttpResponse(modules_string)
        else:
            return HttpResponse('')

@csrf_exempt
def module_edit(request):
    if request.is_ajax():
        module = json.loads(request.body.decode('utf-8'))
        
        if module.get('module_name') == '':
            msg = '模块名称不能为空'
            return HttpResponse(msg)
        if module.get('belong_project') == '请选择':
            msg = '请选择项目，没有请先添加哦'
            return HttpResponse(msg)
        if module.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        p = Project.objects.get(project_name=module.get('belong_project'))
        if module.get('module_name') != Module.objects.get(id=module.get('index')).module_name and \
            Module.objects.filter(module_name=module.get('module_name'), belong_project=p).count()>0:
            msg = "模块已经存在"
            return HttpResponse(msg)
        else:
            m = Module.objects.get(id=module.get('index'))
            m.module_name = module.get('module_name')
            m.belong_project = p
            m.test_user = module.get('test_user')
            m.simple_desc = module.get('simple_desc')
            m.other_desc = module.get('other_desc')
            m.save()
            return HttpResponse(reverse('module_list'))
       

@csrf_exempt
def module_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        project_id = data.get('id')
        module = Module.objects.get(id=project_id)
        module.delete()
        return HttpResponse(reverse('module_list'))


def debugtalk_list(request):
    if request.method == "GET":
        rs = DebugTalk.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'debugtalk': objects }
        return render(request,"debugtalk_list.html",context_dict)


@csrf_exempt
def debugtalk_edit(request, id):
    if request.method == "GET":
        d = DebugTalk.objects.get(pk=id)
        context_dict = {'debugtalk': d.debugtalk, 'id': d.id }
        return render(request, "debugtalk_edit.html",context_dict)

    if request.method == "POST":
        d = DebugTalk.objects.get(pk=id)
        debugtalk = request.POST.get('debugtalk')
        code = debugtalk.replace('new_line', '\r\n')
        d.debugtalk = code
        d.save()
        return redirect(reverse('debugtalk_list'))


@csrf_exempt
def config_add(request):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(request, 'config_add.html', context_dict)
    if request.is_ajax():
        testconfig = json.loads(request.body.decode('utf-8'))
        msg = config_logic(**testconfig)
        if msg == 'ok':
            return HttpResponse(reverse('config_list'))
        else:
            return HttpResponse(msg)


@csrf_exempt
def config_list(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by("-update_time")
        project = request.GET.get("project", "All")
        module = request.GET.get("module", "请选择")
        name = request.GET.get("name",'')
        user = request.GET.get("user",'')
        
        if project == "All":
            if name:
                rs = TestConfig.objects.filter(name=name)
            elif user:
                rs = TestConfig.objects.filter(author=user).order_by("-update_time")
            else:
                rs = TestConfig.objects.all().order_by("-update_time")
        else:
            if module != "请选择":
                m = Module.objects.get(id=module)
                if name:
                    rs = TestConfig.objects.filter(belong_module=m, belong_project=project, name=name)
                elif user:
                    rs = TestConfig.objects.filter(belong_project=project,author=user).order_by("-update_time")
                else:
                    rs = TestConfig.objects.filter(belong_module=m, belong_project=project).order_by("-update_time")
                module = m
                logger.info(module)
                
            else:
                if name:
                    rs = TestConfig.objects.filter(belong_project=project, name=name)
                elif user:
                    rs = TestConfig.objects.filter(belong_project=project, author=user).order_by("-update_time")
                else:
                    rs = TestConfig.objects.filter(belong_project=project).order_by("-update_time")
        info = {'belong_project': project, 'belong_module': module, 'name': name, 'user':user}               
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'config': objects, 'projects': projects, 'info': info}
        return render(request,"config_list.html",context_dict)


@csrf_exempt
def config_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data.get('id')
        config = TestConfig.objects.get(id=config_id)
        config.delete()
        return HttpResponse(reverse('config_list'))


@csrf_exempt
def config_copy(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data['data']['index']
        name = data['data']['name']
        config = TestConfig.objects.get(id=config_id)
        belong_module = config.belong_module
        if TestConfig.objects.filter(name=name, belong_module=belong_module).count() > 0:
            return HttpResponse("配置名称重复")
        else:
            config.name = name
            config.id = None
            config.save()
            return HttpResponse(reverse('config_list'))

@csrf_exempt
def config_edit(request,id):
    if request.method == 'GET':
        config = TestConfig.objects.get(id=id)
        config_request = eval(config.request)
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time'),
            'info': config,
            'request': config_request['config']
        }
        return render(request, 'config_edit.html', context_dict)

    if request.is_ajax():
        testconfig = json.loads(request.body.decode('utf-8'))
        msg = config_logic(type=False, **testconfig)
        if msg == 'ok':
            return HttpResponse(reverse('config_list'))
        else:
            return HttpResponse(msg)

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
        context_dict = {'case': objects, 'projects': projects, 'info':info, 'env':env}
        return render(request,"case_list.html",context_dict)


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

@csrf_exempt
def case_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        case_id = data.get('id')
        case = TestCase.objects.get(id=case_id)
        case.delete()
        return HttpResponse(reverse('case_list'))

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