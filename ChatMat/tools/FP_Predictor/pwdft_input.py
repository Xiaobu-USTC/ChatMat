# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 20:56:48 2023

@author: gaoj
"""
import sys
import warnings
import copy
import os

class Pwdft_input:
    Usage = '''
    请指定 输入文件名 或者 选项名 为参数...
    
    [使用说明]
    
    功能一：用于自动化输出PWDFT的计算输入文件 config.yaml；同时可以将POSCAR转换为yaml格式
	为了不直接覆盖原有的config.yaml文件，新生成的文件名为config.yaml0文件
	并且因为不知道使用者用什么赝势，所以赝势部分要自行修改
        [python直接调用 ]：python pwdft_input.py POSCAR 选项1 选项2 ...
        [ipython方式调用]：  %run pwdft_input.py POSCAR 选项1 选项2 ...
        [选项名称]："POSCAR","detail","md","hyb","ipi"
        
        POSCAR:能够将POSCAR文件转化为yaml格式
        detail:包含更多的细节参数，这些参数不太常用 
        md    :分子动力学参数
        hyb   :杂化泛函参数
        ipi   ：ipi功能参数
        
        以上所有选项都是可选而非必选,但是如果所有的选项都不选择而直接运行此文件，将会打印此使用说明
        若只想打印最基本的参数实现单点能计算
        请输入 python pwdft_input.py basic 或者 %run pwdft_input.py basic
        
        只实现了自己最常用的md部分，其他功能可以自行添加，尤其是detail选项
        
    功能二：用于自动化查看PWDFT的结果输出文件 statfile.0 中的关键信息
    
        -r  :默认文件名为statfile.0
        [python直接调用 ]：python pwdft_input.py -r 选项1 选项2 ...
        [ipython方式调用]：  %run pwdft_input.py -r 选项1 选项2 ...
        
        -rf :后面必须要接上文件名 可以是如 statfile* 这种方式同时查看多个文件
        [python直接调用 ]：python pwdft_input.py -r 文件名 选项1 选项2 ...
        [ipython方式调用]：  %run pwdft_input.py -r 文件名 选项1 选项2 ...
        
        选项名称："norm","step","Ttime"
        
    功能三：用于将PWDFT中分子动力学功能得到的 lastPos.out 文件（bohr为单位）
    或者 MD.xyz 文件 （埃为单位）转换为POSCAR格式文件方便在VESTA中查看
    
        -t  :默认文件名为 pos.txt
        [python直接调用 ]：python pwdft_input.py -t 
        [ipython方式调用]：  %run pwdft_input.py -t 
        
        其中pos.txt文件需要固定的格式
        第一行和POSCAR第一行一样为注释行；第二、三行等同于POSCAR的第六、七行
        第四行和第六行为单位选项；第五行为元胞，第七行开始为原子坐标
        
        这里给出一个单个水分子的案例：
        #h2o
        H O
        2 1
        bohr   
        21.3445
        ang    
        +5.17942889e+00 -2.21271043e+00 +1.64009971e+00
        +4.06862422e+00 -2.20033236e+00 +1.44275784e+00
        +4.60130246e+00 -2.80333828e+00 +1.46880301e+00
        
        其中第四行决定了元胞单位，埃：ang/a; 波尔（原子单位）：bohr/au/pwdft
        第五行 因为PWDFT目前只接受正交的，所以只需要三个数字如 a b c 若三个数相同只需要 a
        第六行决定原子坐标的单位，埃：ang/a/MD; 波尔（原子单位）：bohr/au/lastPos
        第七行开始为原子坐标，需要笛卡尔坐标而不是分数坐标
        
    如果出现报错可能是python版本问题，试一试用 python3 调用
    '''
    def __init__(self,argy):
        self.isdetail   = None
        self.isvdw      = None
        self.isPOSCAR   = None
        self.ismd       = None
        self.ishyb      = None
        self.islrtddft  = None
        self.istddft    = None
        self.isipi      = None
        self.setup(argy)
        self.fopen()
        self.config_print()
        self.fclose()
    
    def setup(self,argy):
           
        if "detail" in argy:
            self.isdetail = True
        if "POSCAR" in argy:
            self.isPOSCAR = True    
        if "md" in argy:
            self.ismd = True
        if "hyb" in argy:
            self.ishyb = True
        if "ipi" in argy:
            self.isipi = True

    
    def config_print(self):
        self.basic_print()
        
        self.iter_print()
        
        if self.ishyb:
            self.hyb_print()
        
        if self.ismd:
            self.md_print()
        
        if self.isipi:
            self.ipi_print()
            
        if self.isPOSCAR:
            self.pos_print()
            
        
    
    def fopen(self):
        self.f_config = open('config.yaml',mode='w',encoding='utf-8')
        if self.isPOSCAR:
            self.f_poscar = open('POSCAR', 'r')
            self.pos2yaml()
    
    def fclose(self):
        self.f_config.close()
        if self.isPOSCAR:
            self.f_poscar.close()
        
    def basic_print(self):
        # 基本输入参数
        self.Hprint("-"*30)
        self.Hprint("Base input parameter for PWDFT")
        self.Hprint("-"*30)
        self.Hprint("")
        
        self.Hprint("Mixing_Variable:  potential; density")
        self.Hprint(["Mixing_Variable","potential"])
        
        self.Hprint("Mixing_Type:  anderson; kerker+anderson; broyden")
        self.Hprint(["Mixing_Type","anderson"])
        
        self.Hprint(["Mixing_StepLength","0.8"])
        self.Hprint(["Mixing_MaxDim","9"])
        
        self.Hprint(["Ecut_Wavefunction","40.0"])
        
        self.Hprint("")
        self.Hprint(["Output_Density","0"])
        self.Hprint(["Output_Wfn","0"])
        self.Hprint(["Restart_Density","0"])
        self.Hprint(["Restart_Wfn","0"])
        
        self.Hprint("")
        self.Hprint(["Temperature","300.0"])
        self.Hprint(["Density_Grid_Factor","2.0"])
        self.Hprint("Smearing_Scheme:  FD; GB; MP")
        self.Hprint(["Smearing_Scheme","FD"])
        self.Hprint(["Extra_Electron","0"])
        
        if self.isvdw:
            self.Hprint("")
            self.Hprint(["VDW_Type","DFT-D2"])
        else:
            self.Hprint("")
            self.Hprint(["VDW_Type","None"])
        
        self.Hprint("")
        self.Hprint("Pseudo_Type:  HGH; ONCV")
        self.Hprint(["Pseudo_Type","ONCV"])
        self.Hprint2("PeriodTable:")
        self.Hprint2("UPF_File:")
        if self.isPOSCAR:
            for i in range(self.atomtype_num):
                str0 = "   -  " + self.atomname_list[i] + "_ONCV_PBE-1.0.upf"
                self.Hprint2(str0)
        
        self.Hprint("")
        self.Hprint(["Use_VLocal","0"])
        self.Hprint(["Use_Atom_Density","0"])
        
        
        if not self.ishyb:
            self.Hprint("")
            self.Hprint("XC_Type:  XC_LDA_XC_TETER93")
            self.Hprint("XC_Type:  XC_GGA_XC_PBE")
            self.Hprint("XC_Type:  XC_HYB_GGA_XC_PBE")
            self.Hprint("XC_Type:  XC_HYB_GGA_XC_HSE06")
            self.Hprint(["XC_Type","XC_LDA_XC_TETER93"])
        
            
        self.Hprint("")
        
    def iter_print(self):
        self.Hprint("-"*30)
        self.Hprint("Iteration parameter for PWDFT")
        self.Hprint("-"*30)
        self.Hprint("")
        
        self.Hprint(["SCF_Inner_Tolerance","1e-4"])
        self.Hprint(["SCF_Inner_MinIter","1"])
        self.Hprint(["SCF_Inner_MaxIter","1"])
        
        self.Hprint("")
        self.Hprint(["SCF_Outer_Tolerance","1e-6"])
        self.Hprint(["SCF_Outer_MinIter","3"])
        self.Hprint(["SCF_Outer_MaxIter","30"])
        
        self.Hprint("")
        self.Hprint(["Calculate_Force_Each_SCF","0"])
        
        self.Hprint("")
        self.Hprint(["Eig_Tolerance","1e-20"])
        self.Hprint(["Eig_MaxIter","3"])
        self.Hprint(["Eig_Min_Tolerance","1e-3"])
        self.Hprint(["Eig_MinIter","2"])
        
        self.Hprint("")
        self.Hprint("PW_Solver:  LOBPCG")
        self.Hprint("PW_Solver:  PPCG")
        self.Hprint("PW_Solver:  CheFSI")
        self.Hprint("PW_Solver:  LOBPCGScaLAPACK")
        self.Hprint("PW_Solver:  PPCGScaLAPACK")
        self.Hprint(["PW_Solver","LOBPCG"])
        
        self.Hprint("")
        self.Hprint(["PPCGsbSize","1"])
        self.Hprint(["ScaLAPACK_Block_Size","32"])
        
        self.Hprint("")
    
    def hyb_print(self):
        self.Hprint("-"*40)
        self.Hprint("Hybrid functional parameters for PWDFT")
        self.Hprint("-"*40)
        self.Hprint("")
        
        self.Hprint(["SCF_Phi_MaxIter","10"])
        self.Hprint("Hybrid_Mixing_Type:  nested; scdiis; pcdiis")
        self.Hprint(["Hybrid_Mixing_Type","nested"])
        self.Hprint(["Hybrid_ACE","1"])
        self.Hprint(["Hybrid_DF","0"])
        self.Hprint("Hybrid_DF_Type:  QRCP; Kmeans; Kmeans+QRCP")
        self.Hprint(["Hybrid_DF_Type","QRCP"])
        self.Hprint(["Hybrid_DF_Num_Mu","6.0"])
        self.Hprint(["Hybrid_DF_Num_GaussianRandom","2.0"])
        
        self.Hprint("")
        self.Hprint("XC_Type:  XC_LDA_XC_TETER93")
        self.Hprint("XC_Type:  XC_GGA_XC_PBE")
        self.Hprint("XC_Type:  XC_HYB_GGA_XC_PBE")
        self.Hprint("XC_Type:  XC_HYB_GGA_XC_HSE06")
        self.Hprint(["XC_Type","XC_HYB_GGA_XC_HSE06"])
    
        self.Hprint("")
        
    def md_print(self):
        self.Hprint("-"*40)
        self.Hprint("Molecular dynamics parameter for PWDFT")
        self.Hprint("-"*40)
        self.Hprint("")
        
        self.Hprint("Ion_Move:  bb; cg; bfgs; fire")
        self.Hprint("Ion_Move:  nosehoover1; verlet; langevin")
        self.Hprint(["Ion_Move","nosehoover1"])
        self.Hprint(["Ion_Max_Iter","0"])
        self.Hprint(["MD_Time_Step","40"])
        self.Hprint(["Ion_Temperature","300.0"])
        
        self.Hprint("")
        self.Hprint("MD_Extrapolation_Type:  linear; quadratic; aspc2; aspc3; xlbomd")
        self.Hprint(["MD_Extrapolation_Type","linear"])
        self.Hprint("MD_Extrapolation_Variable:  density; wavefun")
        self.Hprint(["MD_Extrapolation_Variable","density"])
        
        self.Hprint("")
        self.Hprint(["MD_SCF_Outer_MaxIter","30"])
        if self.ishyb:
            self.Hprint(["MD_SCF_Phi_MaxIter","10"])
        
        self.Hprint("")
        self.Hprint(["Output_Position","0"])
        self.Hprint(["Output_Velocity","0"])
        self.Hprint(["Restart_Position","0"])
        self.Hprint(["Restart_Velocity","0"])
        
        self.Hprint("")
    
        
    def ipi_print(self):
        self.Hprint("-"*30)
        self.Hprint("i-PI parameter for PWDFT")
        self.Hprint("-"*30)
        self.Hprint("")
        
        self.Hprint(["IPI","1"])
        self.Hprint(["Port","31415"])
        self.Hprint(["IPv4","127.0.0.1"])
        self.Hprint(["IPI_Detail","1"])
        
        self.Hprint("")
        self.Hprint("IPI_MD_Extrapolation_Type:  linear; quadratic; aspc2; aspc3; xlbomd")
        self.Hprint(["IPI_MD_Extrapolation_Type","linear"])
        self.Hprint("IPI_MD_Extrapolation_Variable:  density; wavefun")
        self.Hprint(["IPI_MD_Extrapolation_Variable","density"])
        
        self.Hprint("")
        


#---------------------------------------------------------------------------------------        
#---------------------------------------------------------------------------------------    
    def pos_print(self):
        self.Hprint("-"*30)
        self.Hprint("POSCAR for PWDFT")
        self.Hprint("-"*30)
        self.Hprint("")
        
        
        Atom_Type = "[" 
        Atom_Num  = "[" 
        for i in range(self.atomtype_num):
            Atom_Type += " " + str(self.atomtype_list[i]) + ","
            Atom_Num  += " " + self.atomnum_list[i] + ","
        Atom_Type =  Atom_Type[0:len(Atom_Type)-1] + " ]"
        Atom_Num  =  Atom_Num[0:len(Atom_Num)-1] + " ]"
            
        Super_Cell = "[ " + "%.6f" %self.f_supercell[0] + ", " \
                    + "%.6f" %self.f_supercell[1] + ", " \
                    + "%.6f" %self.f_supercell[2] + " ]"
        
        # Atom_pos = [0] * self.atomlist_num
        # for i in range(self.atomlist_num):
        #     Atom_pos[i] = "  -  [ " + "%.8f" %self.f_atompos[i][0] \
        #                 + "  ,  " + "%.8f" %self.f_atompos[i][1] \
        #                 + "  ,  " + "%.8f" %self.f_atompos[i][2] + " ]"
                        
            
        self.Hprint(["Atom_Types_Num",str(self.atomtype_num)])
        self.Hprint(["Atom_Type"     ,Atom_Type])
        self.Hprint(["Atom_Num"      ,Atom_Num])
        self.Hprint(["Super_Cell"    ,Super_Cell])
        self.Hprint(["Atom_Red"      ," "])
        for i in range(self.atomlist_num):
            self.Hprint([self.f_atompos[i][0],self.f_atompos[i][1],self.f_atompos[i][2]],2)
    
    def pos2yaml(self):
        content = self.f_poscar.read()
        lines = content.splitlines()
        zoom  = lines[1]
        f_zoom  = self.str2f(zoom)
        
        cell = [0]*3
        for i in range(3):
            cell[i] = lines[2+i].split()
        f_cell = self.str2f(cell)
        # if f_cell[0][1] != 0 or f_cell[0][2] != 0 \
        #     or f_cell[1][0] != 0 or f_cell[1][2] != 0 \
        #         or f_cell[2][0] != 0 or f_cell[2][1] != 0:
        #             raise Exception("PWDFT只能使用正交晶格...")
        
        f_supercell = [f_zoom*f_cell[0][0]*a2bohr,f_zoom*f_cell[1][1]*a2bohr,f_zoom*f_cell[2][2]*a2bohr]
        
        atomname_list = lines[5].split()
        atomnum_list = lines[6].split()
        if len(atomname_list) != len(atomnum_list):
            raise Exception("! Wrong: len(atomname_list) != len(atomnum_list)")
        atomtype_num = len(atomname_list)
        
        atomtype_list = [0] * atomtype_num
        for i in range(atomtype_num):
            atomtype_list[i] =  PeriodicTable_dict[atomname_list[i]]
        
        if lines[7] == "Selective dynamics":
            crd_type = lines[8]
            len0 = 9
        else:
            crd_type = lines[7]
            len0 = 8
            
        if crd_type == "Direct":
            isc2d = False
        elif crd_type == "Cartesian":
            isc2d = True
        else:
            raise Exception("POSCAR 格式有误")
            
        len1 = int(sum(self.str2f(atomnum_list)))
        atompos = [0]*len1
        for i in range(len1):
            atompos[i] = lines[i+len0].split()
        f_atompos = self.str2f(atompos)
        
        if isc2d:
            for i in range(len1):
                f_atompos[i][0] = f_atompos[i][0]/f_supercell[0]
                f_atompos[i][1] = f_atompos[i][1]/f_supercell[1]
                f_atompos[i][2] = f_atompos[i][2]/f_supercell[2]
        
        if atomtype_num == 2 and "H" in atomname_list and "O" in atomname_list:
            self.isvdw = True
            
        self.atomname_list = atomname_list
        self.atomtype_num  = atomtype_num
        self.atomtype_list = atomtype_list
        self.atomnum_list  = atomnum_list
        self.f_supercell   = f_supercell
        self.f_atompos     = f_atompos
        self.atomlist_num  = len1       
    
    def Hprint(self,a,style=1):
        if style == 1:
            if isinstance(a,str):
                if len(a) == 0:
                    str0 = ""
                else:
                    str0 = "# " + a
            elif isinstance(a,(tuple,list)):
                if len(a) == 2:
                    len1 = len(a[0])
                    str1 = a[0] + " " * (30-len1)
                    str2 = a[1]
                    str0 = str1 + ": " + str2
                else: warnings.warn("! Wrong input for Hprint fuction")   
            
        elif style == 2:
            if isinstance(a,(tuple,list)):
                if a[0] < 0 :
                    str1 = "  -  ["
                else:
                    str1 = "  -  [ "
                if a[1] < 0 :
                    str2 = " , "
                else:
                    str2 = " ,  "
                if a[2] < 0 :
                    str3 = " , "
                else:
                    str3 = " ,  " 
                str0 = str1 + "%.10f" %a[0] + str2 + "%.10f" %a[1] \
                        + str3 + "%.10f" %a[2] + " ]"
                
            else: warnings.warn("! Wrong input for Hprint fuction")
       
        else:
            warnings.warn("! Wrong input for Hprint fuction")
        
        self.f_config.write(str0+"\n")

    def Hprint2(self,a,style=1):
        str0 = ""+a
        self.f_config.write(str0 + "\n")

    def str2f(self,a):
        if isinstance(a, str):
            b = float(a)
        elif isinstance(a, (list,tuple)) and not isinstance(a[0], (list,tuple)):
            b = copy.deepcopy(a)
            for i in range(len(a)):
                b[i] = float(a[i])
        elif isinstance(a, (list,tuple)) and isinstance(a[0], (list,tuple)):
            b = copy.deepcopy(a)
            for i in range(len(a)):
                for j in range(len(a[i])):
                    b[i][j] = float(a[i][j])
        else:
            raise Exception("! Wrong input for str2f fuction")
        
        return b

#---------------------------------------------------------------------------------------        
#--------------------------------------------------------------------------------------- 

    
    @staticmethod
    def shell_print(argy0):
        print("-"*40)
        print("Output information for the statfile.0")
        print("-"*40)
        print("")
        
        #-----------------------------------------------------------------
        filename = []
        if argy0[0] == "-r":
            filename.append("statfile.0")
            for i in range(1,len(argy0)):
                if argy0[i] not in option_list_shell:
                    raise Exception("文件名 或者 选项名 输入错误...")
        elif argy0[0] == "-rf":
            # filename = argy0[1]
            # for i in range(2,len(argy0)):
            #     if argy0[i] not in option_list_shell:
            #         raise Exception("文件名 或者 选项名 输入错误...")
            for i in range(len(argy0)):
                if argy0[i] in option_list_shell:
                    n = i
                    break
            for i in range(1,n):
                filename.append(argy0[i])
                
            for i in range(n,len(argy0)):
                if argy0[i] not in option_list_shell:
                    raise Exception("文件名 或者 选项名 输入错误...")
        #-----------------------------------------------------------------
                
        print("需要查看的文件名：",filename)
        print("-"*40)
        print("Output information for the statfile.0")
        print("-"*40)
        
        if "norm" in argy0:
            for i in range(len(filename)):
                print("")
                os.system("grep 'norm(' " + filename[i] + " -rn")
                # print("grep 'norm(' " + filename[i] + " -rn")
        
        if "step" in argy0:
            for i in range(len(filename)):
                print("")
                os.system("grep 'step' " + filename[i] + " -rn")
                # print("grep 'step' " + filename[i] + " -rn")
        
        if "Ttime" in argy0:
            for i in range(len(filename)):
                print("")
                os.system("grep '! T' " + filename[i] + " -rn")
                # print("grep '! T' " + filename[i] + " -rn")

    @classmethod
    def postxt2POSCAR(cls,argy0):
        f_POSCAR = open('POSCAR0',mode='w',encoding='utf-8')
        f_postxt = open('pos.txt', 'r')
        
        content = f_postxt.read()
        lines = content.splitlines()
        
        comment_line = lines[0]
        
        atomname_list = lines[1].split()
        atomnum_list = lines[2].split()
        if len(atomname_list) != len(atomnum_list):
            raise Exception("! Wrong: len(atomname_list) != len(atomnum_list)")
        len0 = len(atomname_list)
        len1 = int(sum(cls.str2f(cls,atomnum_list)))
        
        cell_type = lines[3]
        cell = lines[4].split()
        if len(cell) == 1:
            f_cell = [float(cell[0])]*3
        elif len(cell) == 3:
            f_cell = cls.str2f(cls,cell)
        else:
            raise Exception("! the input for pos.txt is wrong")
        if cell_type == "ang" or cell_type == "a":
            pass
        elif cell_type == "bohr" or cell_type == "au" or cell_type == "pwdft":
            f_cell[0] = f_cell[0]*bohr2a
            f_cell[1] = f_cell[1]*bohr2a
            f_cell[2] = f_cell[2]*bohr2a
        else:
            raise Exception("! Wrong: ang/a; bohr/au/pwdft;")
            
        pos_type = lines[5]
        pos = []
        for i in range(6,6+len1):
            line = lines[i].split()
            if len(line) == 3:
                line1 = line
            elif len(line) == 4:
                line1 = line[1:]
            else:
                raise Exception("! the input for pos.txt is wrong")
            pos.append(line1)
        f_pos = cls.str2f(cls,pos)
        if pos_type == "ang" or pos_type == "a" or pos_type == "MD":
            num = 1
        elif pos_type == "bohr" or pos_type == "au" or pos_type == "lastPos":
            num = bohr2a
        else:
            raise Exception("! Wrong: ang/a/MD; bohr/au/lastPos;")
        for i in range(len1):
            f_pos[i][0] = f_pos[i][0]/f_cell[0]*num
            f_pos[i][1] = f_pos[i][1]/f_cell[1]*num
            f_pos[i][2] = f_pos[i][2]/f_cell[2]*num
        
        f_POSCAR.write(comment_line+"\n")
        f_POSCAR.write(str(1.0)+"\n")
        f_POSCAR.write(" "*8 + "%.9f" %f_cell[0] + " "*8 + "%.9f" %0 + " "*8 + "%.9f" %0 +"\n")
        f_POSCAR.write(" "*8 + "%.9f" %0 + " "*8 + "%.9f" %f_cell[1] + " "*8 + "%.9f" %0 +"\n")
        f_POSCAR.write(" "*8 + "%.9f" %0 + " "*8 + "%.9f" %0 + " "*8 + "%.9f" %f_cell[0] +"\n")
        
        str1 = ""
        str2 = ""
        for i in range(len0):
            str1 = str1 + " "*4 + atomname_list[i]
            str2 = str2 + " "*4 + atomnum_list[i]
        f_POSCAR.write(str1+"\n")
        f_POSCAR.write(str2+"\n")
        
        f_POSCAR.write("Direct"+"\n")
        
        for i in range(len1):
            f_POSCAR.write(" "*4 + "%.9f" %f_pos[i][0] + " "*8 + "%.9f" %f_pos[i][1] + " "*8 + "%.9f" %f_pos[i][2] + "\n")
        
        f_postxt.close()
        f_POSCAR.close()
        
        
        
bohr2a = 0.529177249     
a2bohr = 1/0.529177249
PeriodicTable_dict = {
    "H": 1,
    "He": 2,
    "Li": 3,
    "Be": 4,
    "B": 5,
    "C": 6,
    "N": 7,
    "O": 8,
    "F": 9,
    "Ne": 10,
    "Na": 11,
    "Mg": 12,
    "Al": 13,
    "Si": 14,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "Ar": 18,
    "K": 19,
    "Ca": 20,
    "Sc": 21,
    "Ti": 22,
    "V": 23,
    "Cr": 24,
    "Mn": 25,
    "Fe": 26,
    "Co": 27,
    "Ni": 28,
    "Cu": 29,
    "Zn": 30,
    "Ga": 31,
    "Ge": 32,
    "As": 33,
    "Se": 34,
    "Br": 35,
    "Kr": 36,
    "Rb": 37,
    "Sr": 38,
    "Y": 39,
    "Zr": 40,
    "Nb": 41,
    "Mo": 42,
    "Tc": 43,
    "Ru": 44,
    "Rh": 45,
    "Pd": 46,
    "Ag": 47,
    "Cd": 48,
    "In": 49,
    "Sn": 50,
    "Sb": 51,
    "Te": 52,
    "I": 53,
    "Xe": 54,
    "Cs": 55,
    "Ba": 56,
    "La": 57,
    "Ce": 58,
    "Pr": 59,
    "Nd": 60,
    "Pm": 61,
    "Sm": 62,
    "Eu": 63,
    "Gd": 64,
    "Tb": 65,
    "Dy": 66,
    "Ho": 67,
    "Er": 68,
    "Tm": 69,
    "Yb": 70,
    "Lu": 71,
    "Hf": 72,
    "Ta": 73,
    "W": 74,
    "Rr": 75,
    "Os": 76,
    "Ir": 77,
    "Pt": 78,
    "Au": 79,
    "Hg": 80,
    "Tl": 81,
    "Pb": 82,
    "Bi": 83,
    "Po": 84,
    "At": 85,
    "Rn": 86,
    "Fr": 87,
    "Ra": 88,
    "Ac": 89,
    "Th": 90,
    "Pa": 91,
    "U": 92,
    "Np": 93,
    "Pu": 94,
    "Am": 95,
    "Cm": 96,
    "Bk": 97,
    "Cf": 98,
    "Es": 99,
    "Fm": 100,
    "Md": 101,
    "No": 102,
    "Lr": 103,
    "Rf": 104,
    "Db": 105,
    "Sg": 106,
    "Bh": 107,
    "Hs": 108,
    "Mt": 109,
    "Ds": 110,
    "Rg": 111,
    "Cn": 112,
    "Uut": 113,
    "Fl": 114,
    "Uup": 115,
    "Lv": 116,
    "Uus": 117,
    "Uuo": 118
}

option_list = ["basic","POSCAR","detail","md","hyb","ipi"]
option_list_shell = ["norm","step","Ttime"]

def pwdft_input():
    argy0 = sys.argv[1:len(sys.argv)]
    if len(argy0) == 0:
        print(Pwdft_input.Usage)
    elif argy0[0] == "-r" or argy0[0] == "-rf":
        Pwdft_input.shell_print(argy0)
    elif argy0[0] == "-t":
        Pwdft_input.postxt2POSCAR(argy0)
    else:
        for i in range(len(argy0)):
            if argy0[i] not in option_list:
                raise Exception("文件名 或者 选项名 输入错误...")
        # print(argy0)
        Pwdft_input(argy0)
    

if __name__ == "__main__":
    
    argy0 = sys.argv[1:len(sys.argv)]
    if len(argy0) == 0:
        print(Pwdft_input.Usage)
    elif argy0[0] == "-r" or argy0[0] == "-rf":
        Pwdft_input.shell_print(argy0)
    elif argy0[0] == "-t":
        Pwdft_input.postxt2POSCAR(argy0)
    else:
        for i in range(len(argy0)):
            if argy0[i] not in option_list:
                raise Exception("文件名 或者 选项名 输入错误...")
        # print(argy0)
        Pwdft_input(argy0)