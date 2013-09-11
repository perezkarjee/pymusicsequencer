using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System;

namespace JSONConConverter
{
    public class JSONCon{
        public enum DataType{
            DInt,
            DFloat,
            DString,
            DList,
            DDictionary
        }
        public JSONCon.DataType type;
        public Int32 di;
        public float df;
        public string ds = "";
        public List<JSONCon> dl = new List<JSONCon>();
        public Dictionary<string, JSONCon> dd = new Dictionary<string, JSONCon>();

        public void Add(JSONCon data)
        {
            if(type == DataType.DList)
            {
                dl.Add(data);
            }
            else
            {
                throw new Exception("This JSONCon object is not a List object!");
            }
        }
        public int Count()
        {
            if(type == DataType.DList)
            {
            }
            else
            {
                throw new Exception("This JSONCon object is not a List object!");
            }
            return dl.Count;
        }
        public void Set(string key, JSONCon data)
        {
            if(type == DataType.DDictionary)
            {
                dd[key] = data;
            }
            else
            {
                throw new Exception("This JSONCon object is not a Dict object!");
            }
        }
        public static JSONCon GetDict(params KeyValuePair<string, JSONCon>[] items)
        {
            JSONCon nd = new JSONCon();
            nd.type = DataType.DDictionary;
            if(items.Length > 0)
            {
                foreach(KeyValuePair<string, JSONCon> data in items)
                {
                    nd.dd[data.Key] = data.Value;
                }
            }
            return nd;
        }
        public static JSONCon GetList(params JSONCon[] items)
        {
            JSONCon nd = new JSONCon();
            nd.type = DataType.DList;
            if(items.Length > 0)
            {
                foreach(JSONCon data in items)
                {
                    nd.dl.Add(data);
                }
            }
            return nd;
        }
        public static JSONCon GetInt(Int32 data)
        {
            JSONCon nd = new JSONCon();
            nd.type = DataType.DInt;
            nd.di = data;
            return nd;
        }
        public static JSONCon GetFloat(float data)
        {
            JSONCon nd = new JSONCon();
            nd.type = DataType.DFloat;
            nd.df = data;
            return nd;
        }
        public static JSONCon GetString(string data)
        {
            JSONCon nd = new JSONCon();
            nd.type = DataType.DString;
            nd.ds = data;
            return nd;
        }

        /*
           Nullable(int? a)
           HasValue
           HasValue는 bool 형식이며, 변수에 null이 아닌 값이 포함되어 있으면 true로 설정됩니다.
           Value
           */

        public static string ConvertToJSON(JSONCon data)
        {
            // 루트는 무조건 리스트 아니면 딕셔너리여야 한다.
            string result2 = "";
            if(data.type == DataType.DInt)
            {
                return data.di.ToString();
            }
            else if(data.type == DataType.DFloat)
            {
                return data.df.ToString();
            }
            else if(data.type == DataType.DString)
            {
                data.ds = data.ds.Replace("\"", "");
                return "\"" + data.ds + "\"";
            }
            else if(data.type == DataType.DList)
            {
                string result = "[";
                for(int i=0; i< data.Count(); ++i)
                {
                    result += JSONCon.ConvertToJSON(data.dl[i]);
                    result += ",";
                }
                if(data.Count() > 0)
                {
                    result = result.Substring(0, result.Length-1);
                }
                return result + "]";
            }
            else if(data.type == DataType.DDictionary)
            {
                string result = "{";
                bool found = false;
                foreach (KeyValuePair<string, JSONCon> pair in data.dd)
                {
                    found = true;
                    result += "\"";
                    result += pair.Key;
                    result += "\"";
                    result += ":";
                    result += JSONCon.ConvertToJSON(pair.Value);
                    result += ",";
                }
                if(found)
                {
                    result = result.Substring(0, result.Length-1);
                }
                return result + "}";
            }
            return result2;

        }

    }
}
