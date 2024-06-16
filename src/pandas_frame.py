import os
import xml.etree.ElementTree as ET
import pandas as pd
import lmfit
import numpy as np
#
import warnings
# RankWarning 경고 무시
warnings.simplefilter('ignore', np.RankWarning)

from src.device_waferno_find_xml import find_xml_files

def pandas_data(device, wafer_nos):
    # 여러 디렉토리 경로
    directories = [
        'dat/HY202103/D07/20190715_190855',
        'dat/HY202103/D08/20190526_082853',
        'dat/HY202103/D08/20190528_001012',
        'dat/HY202103/D08/20190712_113254',
        'dat/HY202103/D23/20190528_101900',
        'dat/HY202103/D23/20190531_072042',
        'dat/HY202103/D23/20190603_204847',
        'dat/HY202103/D24/20190528_105459',
        'dat/HY202103/D24/20190528_111731',
        'dat/HY202103/D24/20190531_151815',
        'dat/HY202103/D24/20190603_225101'
    ]
    # 필터링된 XML 파일 찾기
    xml_files = find_xml_files(directories, device, wafer_nos)

    # 결과를 담을 빈 리스트 초기화
    dfs = []

    # 각 XML 파일에 대해 반복하여 데이터프레임 생성
    for xml_file in xml_files:
        # XML 파일 파싱
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # 데이터 정의를 담을 빈 리스트 초기화
        lot_data = []
        wafer_data = []
        mask_data = []
        testsite_data = []
        name = []
        date = []
        scriptid = []
        operator = []
        row_data = []
        column_data = []
        ErrorFlag_data = []
        ErrorDescription_data = []
        analysiswavelength_data = []
        RsqOfRefSpectrum_data = []
        MaxtransmissionOfRefSpec_data = []
        rsqofIV_data = []
        iatminusoneV_data = []
        iatplusoneV_data = []

        # 각 die에 대한 정보 반복
        for testsiteinfo in root.findall('.//TestSiteInfo'):
            lot_data.append(testsiteinfo.get('Batch'))
            wafer_data.append(testsiteinfo.get('Wafer'))
            mask_data.append(testsiteinfo.get('Maskset'))
            testsite_data.append(testsiteinfo.get('TestSite'))
            row_data.append(testsiteinfo.get('DieRow'))
            column_data.append(testsiteinfo.get('DieColumn'))

            # Operator 데이터 정의
            operator.extend(modulatorsite.get('Operator') for modulatorsite in root.findall('.//ModulatorSite'))
            operator_string = ', '.join(operator)
            operator_data = [operator_string]

            # date 데이터 정의
            date.extend(portcombo.get('DateStamp') for portcombo in root.findall('.//PortCombo'))
            date_string = ', '.join(date)
            date_data = [date_string]

            # Script ID 데이터 정의
            scriptid.extend(designdescription.text for designdescription in root.findall('.//DesignDescription'))
            scriptid_string = ', '.join(scriptid)
            scriptid_data = [scriptid_string]

            # name 데이터 정의
            name.extend(modulator.get('Name') for modulator in root.findall('.//Modulator'))
            name_string = ', '.join(name)
            name_data = [name_string]

            # ErrorFlag 정의
            ErrorFlag_data.append([])

            # ref WavelengthSweep 요소 선택
            WavelengthSweep = list(root.findall('.//WavelengthSweep'))[6]

            # LengthUnit과 transmission 요소의 text 값 가져오기
            length_values = []
            measured_transmission_values = []
            for L in WavelengthSweep.findall('.//L'):
                length_text = L.text
                length_text = length_text.replace(',', ' ')
                length_values.extend([float(value) for value in length_text.split() if value.strip()])

            for IL in WavelengthSweep.findall('.//IL'):
                measured_transmission_text = IL.text
                measured_transmission_text = measured_transmission_text.replace(',', ' ')
                measured_transmission_values.extend(
                    [float(value) for value in measured_transmission_text.split() if value.strip()])

            # 각 차수에 대한 fitting 결과 저장할 리스트 초기화
            fitting_results = []

            # 1차부터 6차까지의 fitting 결과 저장
            for degree in range(1, 7):
                coeffs = np.polyfit(length_values, measured_transmission_values, degree)
                p = np.poly1d(coeffs)
                yhat = p(length_values)
                ybar = np.sum(measured_transmission_values) / len(measured_transmission_values)

                ss_residual = np.sum((measured_transmission_values - yhat) ** 2)
                ss_total = np.sum((measured_transmission_values - ybar) ** 2)
                Rsq = 1 - (ss_residual / ss_total)

                fitting_results.append((degree, Rsq, p))

            # 최적 차수 선택
            best_degree, best_rsq, best_poly = max(fitting_results, key=lambda x: x[1])

            # Rsq 값에 따른 Error Flag 설정
            if best_rsq < 0.997:
                ErrorFlag_data[-1].append(1)
            else:
                ErrorFlag_data[-1].append(0)

            # ErrorDescription 정의
            if ErrorFlag_data[-1][-1] == 0:
                ErrorDescription_data.append('No Error')
            else:
                ErrorDescription_data.append('Ref. spec. Error')

            analysiswavelength_data.append(
                [round(float(AlignWavelength.text), 1) for AlignWavelength in root.findall('.//AlignWavelength')])

            # Ref Spectrum Rsquared, Max Transmission 계산
            RsqOfRefSpectrum_data.append([])
            MaxtransmissionOfRefSpec_data.append([])

            # WavelengthSweep 요소 선택
            WavelengthSweep = list(root.findall('.//WavelengthSweep'))[6]

            # LengthUnit과 transmission 요소의 text 값 가져오기
            length_values = []
            measured_transmission_values = []
            for L in WavelengthSweep.findall('.//L'):
                length_text = L.text
                length_text = length_text.replace(',', ' ')
                length_values.extend([float(value) for value in length_text.split() if value.strip()])

            for IL in WavelengthSweep.findall('.//IL'):
                measured_transmission_text = IL.text
                measured_transmission_text = measured_transmission_text.replace(',', ' ')
                measured_transmission_values.extend(
                    [float(value) for value in measured_transmission_text.split() if value.strip()])

            # 다항식 차수 범위 설정
            poly_degrees = range(1, 7)

            # 각 차수에 대한 fitting 결과 저장할 리스트 초기화
            fitting_results = []

            # 1차부터 6차까지의 fitting 결과 저장
            for degree in range(1, 7):
                coeffs = np.polyfit(length_values, measured_transmission_values, degree)
                p = np.poly1d(coeffs)
                yhat = p(length_values)
                ybar = np.sum(measured_transmission_values) / len(measured_transmission_values)

                ss_residual = np.sum((measured_transmission_values - yhat) ** 2)
                ss_total = np.sum((measured_transmission_values - ybar) ** 2)
                Rsq = 1 - (ss_residual / ss_total)

                fitting_results.append((degree, Rsq, p))

            # 최적 차수 선택
            best_degree, best_rsq, best_poly = max(fitting_results, key=lambda x: x[1])

            # 최적 차수에서만 Rsq 계산
            RsqOfRefSpectrum_data[-1].append(best_rsq)

            # 최댓값 계산
            max_transmission = max(measured_transmission_values)
            MaxtransmissionOfRefSpec_data[-1].append(round(max_transmission, 1))  # 최댓값을 소수점 첫째 자리까지 반올림하여 저장

            # Rsquared of IV, I at -1V, I at 1V 계산
            rsqofIV_data.append([])
            iatminusoneV_data.append([])
            iatplusoneV_data.append([])
            iv_measurement_elements = root.findall('.//IVMeasurement')
            for iv_measurement_element in iv_measurement_elements:
                voltage_text = iv_measurement_element.find('.//Voltage').text
                current_text = iv_measurement_element.find('.//Current').text
                voltage_values = [float(value) for value in voltage_text.split(',')]
                current_values = [float(value) for value in current_text.split(',')]
                current_abs=np.abs(current_values)

                # 적합 실행 (알고리즘 변경)
                def diode_equation(V, Is, n, Vt, V_linear, Ilinear):
                    current = []
                    for v in V:
                        if v >= V_linear:
                            current.append(Is * (np.exp(v / (n * Vt)) - 1))
                        else:
                            current.append(Ilinear * v)
                    return current

                # 초기 추정값 설정
                Is_guess = current_abs[0]
                n_guess = 1.0
                Vt_guess = 0.0256
                Ilinear_guess = 0.0
                Vlinear_guess = 0.0

                # 매개변수 및 초기 추정값 정의
                params = lmfit.Parameters()
                params.add('Is', value=Is_guess, min=0)  # 포화 전류
                params.add('n', value=n_guess, min=1)  # 이상성 지수
                params.add('Vt', value=Vt_guess, min=0)  # 열전압
                params.add('Ilinear', value=Ilinear_guess)  # 음수 전압 영역에서의 전류
                params.add('V_linear', value=Vlinear_guess)  # 음수 전압 영역에서의 선형 근사 전압

                result = lmfit.minimize(
                    lambda params, x, y: np.array(diode_equation(x, **params)) - np.array(y),
                    params, args=(voltage_values, current_values),
                    method='least squares'
                )

                best_fit = np.abs(current_values) + result.residual
                ss_residual = np.sum(result.residual ** 2)
                ss_total = np.sum(np.abs(current_values) - np.abs(np.mean(current_values)) ** 2)
                rsqofIV_data[-1].append(1 - (ss_residual / ss_total))

                voltage_index_minus1V = voltage_values.index(-1.0)
                current_minus1V = current_values[voltage_index_minus1V]

                # 전압이 -1V일 때의 전류 값
                # 절댓값 취하고 - 부호 붙힘.
                current_minus1V = np.abs(current_values[voltage_index_minus1V]) * (-1)
                iatminusoneV_data[-1].append(current_minus1V)

                # 전압이 1V일 때의 전류 값
                voltage_index_1V = voltage_values.index(1.0)
                # 절댓값 취함
                current_1V = np.abs(current_values[voltage_index_1V])
                iatplusoneV_data[-1].append(current_1V)

            # 리스트를 문자열로 변환하는 함수
            def list_to_string(lst):
                return ', '.join(map(str, lst))

            # 변환된 데이터를 저장할 리스트
            converted_ErrorFlag_data = [list_to_string(sublist) for sublist in ErrorFlag_data]
            converted_Analysiswavelength_data = [list_to_string(sublist) for sublist in analysiswavelength_data]
            converted_RsqOfRefSpectrum_data = [list_to_string(sublist) for sublist in RsqOfRefSpectrum_data]
            converted_MaxtransmissionOfRefSpec_data = [list_to_string(sublist) for sublist in MaxtransmissionOfRefSpec_data]
            converted_rsqofIV_data = [list_to_string(sublist) for sublist in rsqofIV_data]
            converted_iatminusoneV_data = [list_to_string(sublist) for sublist in iatminusoneV_data]
            converted_iatplusoneV_data = [list_to_string(sublist) for sublist in iatplusoneV_data]

        # 데이터프레임 생성
        df = pd.DataFrame({
            'Lot': lot_data,
            'Wafer': wafer_data,
            'Mask': mask_data,
            'TestSite': testsite_data,
            'Name': name_data,
            'Date': date_data,
            'Script ID': scriptid_data,
            'Operator': operator_data,
            'Row': row_data,
            'Column': column_data,
            'ErrorFlag': converted_ErrorFlag_data,
            'ErrorDescription': ErrorDescription_data,
            'Analysis Wavelength': converted_Analysiswavelength_data,
            'Rsq of Ref. spectrum (Nth)': converted_RsqOfRefSpectrum_data,
            'Max transmission of Ref. spec. (dB)': converted_MaxtransmissionOfRefSpec_data,
            'Rsq of IV': converted_rsqofIV_data,
            'I at -1V [A]': converted_iatminusoneV_data,
            'I at 1V [A]': converted_iatplusoneV_data
        })

        # 결과 데이터프레임을 리스트에 추가
        dfs.append(df)

    if not dfs:
        raise ValueError(f"No objects to concatenate for device {device} and wafer {wafer_nos}")

    # 모든 XML 파일에 대한 데이터프레임을 합치기
    final_df = pd.concat(dfs, ignore_index=True)

    # 특정 열의 값을 실수 형태로 변환
    for column in columns_to_convert:
        if column in final_df.columns:
            final_df[column] = pd.to_numeric(final_df[column], errors='coerce')

    # 결과 데이터프레임 반환
    return final_df

# 변환할 열 리스트
columns_to_convert = ['ErrorFlag',
                      'AnotherColumn',
                      'Row',
                      'Column',
                      'Rsq of Ref. spectrum (Nth)',
                      'Max transmission of Ref. spec. (dB)',
                      'Rsq of IV',
                      'I at -1V [A]',
                      'I at 1V [A]']

def save_to_excel(df, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    df.to_excel(filepath, index=False)