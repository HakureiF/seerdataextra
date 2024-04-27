import json

file1 = open("./data/move_stones.json", "r", encoding="utf-8")
moves_stones = json.load(file1)
file1.close()

file2 = open("./data/moves.json", "r", encoding="utf-8")
moves = json.load(file2)
file2.close()

file3 = open("./data/effectInfo.json", "r", encoding="utf-8")
effectInfo = json.load(file3)
file3.close()


effect_dict = {}
paramType_dict = {}
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

for move in moves['MovesTbl']['Moves']['Move']:
    #遍历每一个技能
    if 'SideEffect' in move and move['ID'] < 38000:
        tmp = move['SideEffect']
        # 技能效果id
        effects = [] 
        if isinstance(tmp, int):
            effects.append(tmp)
        if isinstance(tmp, str):
            tmps = tmp.split(" ")
            effects.extend([int(t) for t in tmps if t])

        # 技能效果参数      
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
                if effect not in effect_dict:
                    break
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
            full_info = f"[{move['Name']}]：" + ','.join(move_info)
            move['FullInfo'] = full_info
            # print(full_info)


move_dict = {}
for m in moves['MovesTbl']['Moves']['Move']:
    if 'FullInfo' in m:
        move_dict[m['ID']] = m['FullInfo']
    else:
        move_dict[m['ID']] = f"[{m['Name']}]"

for stone in moves_stones['MoveStones']['MoveStone']:
    move_dict[stone['ID']] = f"[{stone['Name']}]"

with open('moves_jsondata.json', 'w', encoding='utf-8') as f:
    json.dump(move_dict, f, ensure_ascii=False)