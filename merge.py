import json
import traceback

file1 = open("./data/monsters.json", "r", encoding="utf-8")
monsters = json.load(file1)
file1.close()

file2 = open("./data/moves.json", "r", encoding="utf-8")
moves = json.load(file2)
file2.close()

file3 = open("./manualdata/effectInfo_modify.json", "r", encoding="utf-8")
effectInfo = json.load(file3)
file3.close()

file4 = open("./data/effectIcon.json", "r", encoding="utf-8")
effectIcon = json.load(file4)
file4.close()

file5 = open("./data/skillTypes.json", "r", encoding="utf-8")
skillTypes = json.load(file5)
file5.close()

def get_type_name(type_id: int) -> str:
    for item in skillTypes['root']['item']:
        if type_id == item['id']:
            return item['cn']


effect_dict = {}
paramType_dict = {}
icon_dict = {}
for t in effectInfo['root']['ParamType']:
    if 'params' in t and isinstance(t['params'], str):
        param_str = t['params']
        params = param_str.split("|")
        tmp = t
        tmp['params'] = params
        paramType_dict[t['id']] = tmp
    else:
        paramType_dict[t['id']] = t
    
for e in effectInfo['root']['Effect']:
    if 'param' in e:
        param_str = e['param']
        params = param_str.split("|")
        tmp = e
        tmp['params'] = params
        effect_dict[e['id']] = tmp
    else:
        effect_dict[e['id']] = e
    
for i in effectIcon['root']['effect']:
    if 'petId' in i:
        if isinstance(i['petId'], str):
            continue
        
        if i['petId'] in icon_dict:
            icon_dict[int(i['petId']) + 5000] = i
        else:
            icon_dict[i['petId']] = i
    
# 处理技能效果描述
for move in moves['MovesTbl']['Moves']['Move']:
    if 'SideEffect' in move and move['ID'] < 38000:
        tmp = move['SideEffect']
        effects = [] #技能代码数组
        if isinstance(tmp, int):
            effects.append(tmp)
        if isinstance(tmp, str):
            tmps = tmp.split(" ")
            effects.extend([int(t) for t in tmps if t])
                    
        if 'SideEffectArg' in move:
            tmp2 = move['SideEffectArg']
            args = [] #技能效果参数
            if isinstance(tmp2, int):
                args.append(tmp2)
            if isinstance(tmp2, str):
                tmps2 = tmp2.split(" ")
                args.extend([int(t) for t in tmps2 if t])
                
            move_info = [] #每条技能代码对应的描述存放的数组
            curr_arg = 0 #指针指向当前处理的技能效果参数
            for effect in effects:
                if effect not in effect_dict:
                    break
                argsNum = effect_dict[effect]['argsNum'] #技能代码effect需要的参数数量
                info = effect_dict[effect]['info'] #技能代码effect对应的插入参数前的描述文本
                
                if 'params' in effect_dict[effect]:
                    params = effect_dict[effect]['params'] #上面已经处理过的技能代码effect的参数的数组
                    for param in params:
                        param_set = param.split(',') #param_set是长度为3的数组，其中：0 参数类型的id 1 参数索引 2 Unknown
                        paramType = paramType_dict[int(param_set[0])]
                        index = int(param_set[1])
                        if int(param_set[0]) == 0: #类型1有6个参数表示各项强化
                            info = info.replace('{'+str(index)+'}', '{}{}{}{}{}{}'.format(*['{'+str(i)+'}' for i in range(index, index+6)]))
                            for i in range(curr_arg + index, curr_arg + index + 6): #遍历每项强化
                                if args[i] == 0:
                                    args[i] = ''
                                else:
                                    args[i] = paramType['params'][i - curr_arg - index] + f'+{args[i]}'
                                                                
                        if int(param_set[0]) in [1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,21]: #全部是数值可直接带入的参数类型
                            args[curr_arg + index] = paramType['params'][args[curr_arg + index]]
                            
                        if int(param_set[0]) == 14: #需要补充加或减号
                            if args[curr_arg + index] > 0:
                                args[curr_arg + index] = '+' + str(args[curr_arg + index])
                        
                        if int(param_set[0]) == 20: #回pp参数类型
                            if args[curr_arg + index] >= 40:
                                args[curr_arg + index] = '全部'
                            else:
                                args[curr_arg + index] = paramType['params'][args[curr_arg + index]]
                
                try:
                    ef_info = info.format(*args[curr_arg: curr_arg+argsNum])
                except IndexError:
                    ef_info = info

                
                curr_arg = curr_arg + argsNum
                move_info.append(ef_info)
            
            if 'MustHit' in move:
                move_info.insert(0, '必中')
            elif 'Accuracy' in move:
                move_info.insert(0, f"命中率{move['Accuracy']}%")
            if 'MaxPP' in move:
                move_info.insert(0, f"pp{move['MaxPP']}")
            if 'Power' in move:
                move_info.insert(0, f"威力{move['Power']}")
            full_info = f"【{move['Name']}】：" + '；'.join(move_info)
            move['FullInfo'] = full_info


move_dict = {}
for m in moves['MovesTbl']['Moves']['Move']:
    move_dict[m['ID']] = m
    

for monster in monsters['Monsters']['Monster']:
    if monster['ID'] > 5000 or monster['ID'] < 2000:
        continue
    
    #普通技能
    for move in monster['LearnableMoves']['Move']:
        if 'Rec' in move:
            move['Detail'] = move_dict[move['ID']]
    #特训技能
    if 'SpMove' in monster['LearnableMoves']:
        for move in monster['LearnableMoves']['SpMove']:
            move['Detail'] = move_dict[move['ID']]
    #神谕技能
    if 'AdvMove' in monster['LearnableMoves']:
        if isinstance(monster['LearnableMoves']['AdvMove'], list):
            for move in monster['LearnableMoves']['AdvMove']:
                move['Detail'] = move_dict[move['ID']]
        else:
            monster['LearnableMoves']['AdvMove']['Detail'] = move_dict[monster['LearnableMoves']['AdvMove']['ID']]
    #第五技能
    if 'ExtraMoves' in monster:
        monster['ExtraMoves']['Move']['Detail'] = move_dict[monster['ExtraMoves']['Move']['ID']]
    #额外第五技能 
    if 'SpExtraMoves' in monster:
        if isinstance(monster['SpExtraMoves']['Move'], list):
            # print(json.dumps(monster, ensure_ascii=False))
            for i in range(len(monster['SpExtraMoves']['Move'])):
                monster['SpExtraMoves']['Move'][i]['Detail'] = move_dict[monster['SpExtraMoves']['Move'][i]['ID']]
            # print(json.dumps(monster, ensure_ascii=False))
        else:
            monster['SpExtraMoves']['Move']['Detail'] = move_dict[monster['SpExtraMoves']['Move']['ID']]
        
        
    #原生魂印
    if monster['ID'] in icon_dict:
        monster['Icon'] = icon_dict[monster['ID']]
    #羁绊神谕等进阶魂印
    if monster['ID'] + 5000 in icon_dict:
        monster['SpIcon'] = icon_dict[monster['ID'] +5000]
    
        
f = open('pets_jsondata.json', 'w', encoding="utf-8")

pets_jsondata = {}

for monster in monsters['Monsters']['Monster']:
    if monster['ID'] > 5000 or monster['ID'] < 2000:
        continue
    
    pet_data = ''
    
    pet_data += f"{monster['DefName']}\n"
    pet_data += f"{get_type_name(monster['Type'])}\n"
    if 'Icon' in monster and monster['Icon']['tips']:
        pet_data += '魂印：' + monster['Icon']['tips'] + "\n"
    
    if 'SpIcon' in monster and monster['SpIcon']['tips']:
        pet_data += '进阶魂印：' + monster['SpIcon']['tips'] + "\n"
    
    # f.write('\n技能效果：\n')
    for move in monster['LearnableMoves']['Move']:
        if 'Detail' in move:
            if 'FullInfo' in move['Detail']:
                text = move['Detail']['FullInfo']
                pet_data += text + '\n'
    if 'AdvMove' in monster['LearnableMoves']:
        if isinstance(monster['LearnableMoves']['AdvMove'], list):
            for move in monster['LearnableMoves']['AdvMove']:
                if 'FullInfo' in move['Detail']:
                    text = move['Detail']['FullInfo']
                    pet_data += text + '\n'
        else:
            pet_data += monster['LearnableMoves']['AdvMove']['Detail']['FullInfo'] + '\n'
    if 'SpMove' in monster['LearnableMoves']:
        for move in monster['LearnableMoves']['SpMove']:
            if 'Detail' in move:
                if 'FullInfo' in move['Detail']:
                    text = move['Detail']['FullInfo']
                    pet_data += text + '\n'
            
    
    if 'ExtraMoves' in monster:
        # f.write('第五技能效果：\n')
        move = monster['ExtraMoves']['Move']['Detail']
        if 'FullInfo' in move:
            pet_data += move['FullInfo'] + '\n'
    if 'SpExtraMoves' in monster:
        # f.write('额外第五技能效果：\n')
        if isinstance(monster['SpExtraMoves']['Move'], list):
            for m in monster['SpExtraMoves']['Move']:
                move = m['Detail']
                if 'FullInfo' in move:
                    pet_data += move['FullInfo'] + '\n'
        else:
            move = monster['SpExtraMoves']['Move']['Detail']
            if 'FullInfo' in move:
                pet_data += move['FullInfo'] + '\n'
    
    if pet_data.__contains__("【"):
        pets_jsondata[monster['ID']] = pet_data

json.dump(pets_jsondata, f, ensure_ascii=False)
        
f.close()