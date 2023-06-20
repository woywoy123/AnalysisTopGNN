from .String import String
from .General import Tools


class Tables(Tools):
    def __init__(self):
        self._S = " | "
        self._Columns = {}
        self._Rows = {}
        self._matrix = {}
        self.Sum = True
        self.MinMax = False
        self.Title = None

    def AddRowTitle(self, Title, Unit=False):
        self._Rows[Title] = Title
        if Unit:
            self._Rows[Title] += "(" + str(Unit) + ")"

    def AddColumnTitle(self, Title, Unit=False):
        self._Columns[Title] = Title
        if Unit:
            self._Columns[Title] += "(" + str(Unit) + ")"

    def AddValues(self, RowTitle, ColumnTitle, Val, RowUnit=False, ColUnit=False):
        RowTitle = str(RowTitle)
        ColumnTitle = str(ColumnTitle)
        self.AddRowTitle(RowTitle, RowUnit)
        self.AddColumnTitle(ColumnTitle, ColUnit)
        if RowTitle not in self._matrix:
            self._matrix[RowTitle] = {}
        if ColumnTitle not in self._matrix[RowTitle]:
            self._matrix[RowTitle][ColumnTitle] = []
        self._matrix[RowTitle][ColumnTitle].append(Val)

    def AlignColumns(self, inpt):
        cols = []
        for i in inpt:
            splitter = i.split(self._S)
            tmp = [len(k) for k in splitter]
            if len(cols) == 0:
                cols = tmp
            cols = [c if c >= s else s for s, c in zip(cols, tmp)]
        for i in range(len(inpt)):
            splitter = inpt[i].split(self._S)
            inpt[i] = self._S.join(
                [s + " " * (k - len(s)) for s, k in zip(splitter, cols)]
            )
        return inpt

    def Compile(self):
        def Transformer(inpt, row, col):
            rinpt = ""
            cinpt = ""
            if row not in inpt:
                return ""
            if col not in inpt[row]:
                return ""
            out = inpt[row][col][0]
            out = sum(inpt[row][col]) if self.Sum else out
            return out

        def ColMargin():
            out_s = {}
            out_n = {}
            all_s = 0
            for row in self._matrix:
                s = sum(list(self.MergeNestedList(list(self._matrix[row].values()))))
                out_s[row] = s
                out_n[row] = s
                all_s += s
            for row in out_n:
                if all_s == 0:
                    all_s = 1
                out_n[row] = str(round(100 * float(out_n[row] / all_s), 4))
            return out_s, out_n

        def RowMargin():
            o_s, _ = ColMargin()
            s = sum(list(self.MergeNestedList(list(o_s.values()))))

            dic_col = {}
            for row in self._matrix:
                for col in self._matrix[row]:
                    if col not in dic_col:
                        dic_col[col] = 0
                    dic_col[col] += sum(self._matrix[row][col])
            dic_col_sum = {}
            for col in dic_col:
                dic_col_sum[col] = dic_col[col]
                dic_col[col] = round(100 * float(dic_col[col] / s), 4)

            return dic_col_sum, dic_col

        def ColMarginMax():
            Min_dict = {}
            Max_dict = {}
            rvec = []
            for col in self._Columns:
                for r in self._matrix:
                    if col not in self._matrix[r]:
                        continue
                    if col not in Min_dict:
                        Min_dict[col] = []
                    if col not in Max_dict:
                        Max_dict[col] = []
                    rvec.append(r)
                    Max_dict[col] += self._matrix[r][col]
                    Min_dict[col] += self._matrix[r][col]
            for col in self._Columns:
                if col not in Max_dict:
                    continue
                max_ = max(Max_dict[col])
                min_ = min(Min_dict[col])
                Max_dict[col] = [max_, rvec[Max_dict[col].index(max_)]]
                Min_dict[col] = [min_, rvec[Min_dict[col].index(min_)]]
            return Max_dict, Min_dict

        rows = list(self._matrix)
        marg_row_s, marg_row_p = ColMargin()
        output = [self._S.join(self._Columns.keys())]
        output[-1] += (
            str(self._S + " Sum " + self._S + " fraction (%) ") if self.Sum else ""
        )
        for r in rows:
            s = (
                r
                + self._S
                + self._S.join(
                    [
                        str(Transformer(self._matrix, r, c))
                        for c in list(self._Columns)[1:]
                    ]
                )
            )
            s += (
                str(self._S + str(marg_row_s[r]) + self._S + marg_row_p[r])
                if self.Sum
                else ""
            )
            output += [s]

        if self.Sum:
            col_mrg_s, col_mrg_p = RowMargin()
            output += [
                "Sum of Column"
                + self._S
                + self._S.join([str(s) for s in col_mrg_s.values()])
                + self._S
                + self._S
            ]
            output += [
                "fraction (%)"
                + self._S
                + self._S.join([str(s) for s in col_mrg_p.values()])
                + self._S
                + self._S
            ]
        if self.MinMax:
            Max, Min = ColMarginMax()
            output += [
                "Minimum Value"
                + self._S
                + self._S.join(
                    [str(s[0]) + " (@ " + str(s[1]) + ")" for s in Min.values()]
                )
            ]
            output += [
                "Maximum Value"
                + self._S
                + self._S.join(
                    [str(s[0]) + " (@ " + str(s[1]) + ")" for s in Max.values()]
                )
            ]

        output = self.AlignColumns(output)

        spl = output[0].split(self._S)
        output.insert(
            1,
            "+".join(
                [
                    "-" * (len(s) + 1 if i == 0 else len(s) + 2)
                    for i, s in zip(range(len(spl)), spl)
                ]
            ),
        )
        output.insert(
            -2 if self.Sum or self.MinMax else len(output),
            "+".join(
                [
                    "-" * (len(s) + 1 if i == 0 else len(s) + 2)
                    for i, s in zip(range(len(spl)), spl)
                ]
            ),
        )
        output.insert(
            0,
            "=" * (int(len(output[0]) / 2) - len(str(self.Title)))
            + " "
            + str(self.Title)
            + " "
            + "=" * (int(len(output[0]) / 2)),
        )
        self.output = output

    def DumpTableToFile(self, Directory):
        directory = "/".join(Directory.split("/")[:-1])
        self.mkdir(directory)
        Directory = self.AddTrailing(Directory, ".txt")
        F = open(Directory, "w")
        F.write("\n".join(self.output))
        F.close()
