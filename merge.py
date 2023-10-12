import json
import traceback

file1 = open("./data/monsters.json", "r", encoding="utf-8")
monsters = json.load(file1)
file1.close()

file2 = open("./data/moves.json", "r", encoding="utf-8")
moves = json.load(file2)
file2.close()

file3 = open("./data/effectInfo.json", "r", encoding="utf-8")
effectInfo = json.load(file3)
file3.close()

file4 = open("./data/effectIcon.json", "r", encoding="utf-8")
effectIcon = json.load(file4)
file4.close()


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
    
#
for move in moves['MovesTbl']['Moves']['Move']:
    if 'SideEffect' in move and move['ID'] < 38000:
        tmp = move['SideEffect']
        effects = [] 
        if isinstance(tmp, int):
            effects.append(tmp)
        if isinstance(tmp, str):
            tmps = tmp.split(" ")
            effects.extend([int(t) for t in tmps if t])
                    
        if 'SideEffectArg' in move:
            tmp2 = move['SideEffectArg']
            args = [] 
            if isinstance(tmp2, int):
                args.append(tmp2)
            if isinstance(tmp2, str):
                tmps2 = tmp2.split(" ")
                args.extend([int(t) for t in tmps2 if t])
                
            move_info = []
            curr_arg = 0
            for effect in effects:
                argsNum = effect_dict[effect]['argsNum']
                info = effect_dict[effect]['info']
                
                if 'params' in effect_dict[effect]:
                    params = effect_dict[effect]['params']
                    for param in params:
                        # param 0——ParamType 1——Index 2——Unknown
                        param_set = param.split(',')
                        paramType = paramType_dict[int(param_set[0])]
                        index = int(param_set[1])
                        if int(param_set[0]) == 0:
                            info = info.replace('{'+str(index)+'}', '{}{}{}{}{}{}'.format(*['{'+str(i)+'}' for i in range(index, index+6)]))
                            for i in range(curr_arg + index, curr_arg + index + 6):
                                if args[i] == 0:
                                    args[i] = ''
                                else:
                                    args[i] = paramType['params'][i - curr_arg - index]
                                    
                        if int(param_set[0]) in [1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,21]:
                            args[curr_arg + index] = paramType['params'][args[curr_arg + index]]
                            
                        if int(param_set[0]) == 14:
                            if args[curr_arg + index] > 0:
                                args[curr_arg + index] = '+' + str(args[curr_arg + index])
                        
                        if int(param_set[0]) == 20:
                            if args[curr_arg + index] >= 40:
                                args[curr_arg + index] = '全部'
                            else:
                                args[curr_arg + index] = paramType['params'][args[curr_arg + index]]
                
                ef_info = info.format(*args[curr_arg: curr_arg+argsNum])

                
                curr_arg = curr_arg + argsNum
                move_info.append(ef_info)
            
            full_info = "技能[" + move['Name'] + "]的效果是：" + ','.join(move_info)
            
            move['FullInfo'] = full_info


move_dict = {}
for m in moves['MovesTbl']['Moves']['Move']:
    move_dict[m['ID']] = m
    

for monster in monsters['Monsters']['Monster']:
    if monster['ID'] > 5000:
        break
    
    #普通技能
    for move in monster['LearnableMoves']['Move']:
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
        monster['SpExtraMoves']['Move']['Detail'] = move_dict[monster['SpExtraMoves']['Move']['ID']]
        
        
    #原生魂印
    if monster['ID'] in icon_dict:
        monster['Icon'] = icon_dict[monster['ID']]
    #羁绊神谕等进阶魂印
    if monster['ID'] + 5000 in icon_dict:
        monster['SpIcon'] = icon_dict[monster['ID'] +5000]
        
    if monster['ID'] == 5000:
        print(monster)