import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import soot.Body;
import soot.PatchingChain;
import soot.Scene;
import soot.SootClass;
import soot.SootMethod;
import soot.Unit;
import soot.Value;
import soot.jimple.AssignStmt;
import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.options.Options;
import soot.tagkit.AnnotationTag;
import soot.tagkit.VisibilityAnnotationTag;
import soot.toolkits.graph.BriefUnitGraph;
import soot.toolkits.graph.PseudoTopologicalOrderer;
import soot.toolkits.graph.UnitGraph;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.opencsv.CSVWriter;


public class TestAnalyzer {

	static String className = "Wish.RepresentativeTests";
	static String outputFile = null;
	static String sootClassPath = "/Users/felicitia/Documents/workspaces/Eclipse/TestBenchmark/target/classes";
	static String appiumPath = "/Users/felicitia/Documents/Research/Android_Testing_Research/java-client-7.0.0.jar";
	
	static String testDir = "/Users/felicitia/Documents/workspaces/Eclipse/TestAnalyzer/src/test_csv/";
	
	static SootClass sootClass = null;
	static SootMethod method = null;
	static List<Body> testBodyList = null;

	static String LINE_TAG = "LineNumberTag";
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		sootSetting();
//		add test body to testBodyList
		testBodyList = new ArrayList<Body>();
		for (SootMethod method: sootClass.getMethods()){
			VisibilityAnnotationTag tag = (VisibilityAnnotationTag) method.getTag("VisibilityAnnotationTag");
			if(tag != null){
				for (AnnotationTag annotation : tag.getAnnotations()) {
					 if (annotation.getType().equals("Lorg/testng/annotations/Test;")) {
						 System.out.println(method.toString() + " is added to body list...");
						 testBodyList.add(method.retrieveActiveBody());
					 }
				}
			}
		}
//		for(Body body: testBodyList){
//			if(body.getMethod().toString().contains("testAddress"))
//			printAllUnits(body);
//		}
		writeTest2File();
	}
	
	public static void writeTest2File(){
		File file = new File(testDir + sootClass.getPackageName() + ".csv");
		// create FileWriter object with file as parameter 
        FileWriter outputfile;
		try {
			outputfile = new FileWriter(file, true); //true for appending to file
			CSVWriter writer = new CSVWriter(outputfile); 
			for(Body body: testBodyList){
//				if(!body.getMethod().toString().contains("testAddress")){
//					continue;
//				}
				List<String> line = new ArrayList<String>();
				line.add(body.getMethod().toString());
				line.add(analyzeTest(body).toString());
				String[] lineArray = new String[line.size()];
				lineArray = line.toArray(lineArray);
				writer.writeNext(lineArray);
				System.out.println("finished writing " + body.getMethod() + " to csv file :)" );
			}
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
	}

	public static JsonArray analyzeTest(Body body){
		JsonArray eventArray = new JsonArray();
		Gson gson = new Gson();
		UnitGraph sootCfg = new BriefUnitGraph(body);
		PseudoTopologicalOrderer pto = new PseudoTopologicalOrderer();
		List jTopoOrder = pto.newList(sootCfg);
		Map<String, String> inputMap = new HashMap<String, String>();
		Map<String, String> guiMap = new HashMap<String, String>();
		
		for(Object unit: jTopoOrder){
			Stmt stmt = (Stmt) unit;
			
//			add sendKeys GUIEvent
			if(stmt.toString().contains("io.appium.java_client.android.AndroidElement: void sendKeys")){
				GUIEvent event = new GUIEvent();
				event.action = GUIEvent.sendKeys;
				InvokeExpr invoke = stmt.getInvokeExpr();
				event.input = inputMap.get(invoke.getArg(0).toString()); 
				String caller = getStrInBrackets(invoke.getUseBoxes().get(0).toString());
				event.id_or_xpath = guiMap.get(caller);
				eventArray.add(gson.toJson(event));
				System.out.println("successfully analyzed: "+ stmt);
				continue;
			}
//			add click GUIEvent
			if(stmt.toString().contains("io.appium.java_client.android.AndroidElement: void click")){
				GUIEvent event = new GUIEvent();
				event.action = GUIEvent.click;
				InvokeExpr invoke = stmt.getInvokeExpr();
				String caller = getStrInBrackets(invoke.getUseBoxes().get(0).toString());
				event.id_or_xpath = guiMap.get(caller);
				eventArray.add(gson.toJson(event));
				System.out.println("successfully analyzed: " + stmt);
				continue;
			}
			
//			add xpath to guiDic
			if(stmt.toString().contains("io.appium.java_client.android.AndroidDriver: org.openqa.selenium.WebElement findElementByXPath(java.lang.String)")){
				AssignStmt assign = (AssignStmt) stmt;
				InvokeExpr invoke = stmt.getInvokeExpr();
				guiMap.put(assign.getLeftOp().toString(), "xpath@" + getStrInQuotes(invoke.getArg(0).toString()));
				System.out.println("successfully analyzed:" + stmt);
				continue;
			}
//			add resource id to guiDic
			if(stmt.toString().contains("io.appium.java_client.android.AndroidDriver: org.openqa.selenium.WebElement findElementById(java.lang.String)")){
				AssignStmt assign = (AssignStmt) stmt;
				InvokeExpr invoke = stmt.getInvokeExpr();
				guiMap.put(assign.getLeftOp().toString(), "id@" + getStrInQuotes(invoke.getArg(0).toString()));
				System.out.println("successfully analyzed:" + stmt);
				continue;
			}
			
//			update guiMap with new key (when the variable name changes due to an assign statement to convert type)
			String key = getKeyInStmt(guiMap, stmt.toString());
			if( key != null && stmt instanceof AssignStmt){
				String value = guiMap.get(key);
				guiMap.remove(key);
				AssignStmt assign = (AssignStmt) stmt;
				guiMap.put(assign.getLeftOp().toString(), value);
				System.out.println("successfully analyzed: " + stmt);
				continue;
			}
//			add input value to inputDic
			if(stmt instanceof AssignStmt){
				AssignStmt assign = (AssignStmt) stmt;
				Value value = assign.getRightOp();
				if(value instanceof StringConstant){
					int idx = assign.getLeftOp().toString().indexOf("[");
					if(idx != -1){
						inputMap.put(assign.getLeftOp().toString().substring(0, idx), getStrInQuotes(value.toString()));
					}else{
						inputMap.put(assign.getLeftOp().toString(), getStrInQuotes(value.toString()));
					}
					System.out.println("successfully analyzed: " + stmt);
					continue;
				}
			}

		}
	
		return eventArray;
	}
	
	public static void printAllUnits(Body body){
		final PatchingChain<Unit> units = body.getUnits();
		for (Iterator<Unit> iter = units.snapshotIterator(); iter.hasNext();) {
			final Stmt stmt = (Stmt) iter.next();
				System.out.println("stmt: "+stmt);
		}		
	}
	
	public static void sootSetting() {
		sootClassPath = Scene.v().getSootClassPath() + File.pathSeparator + sootClassPath;
		Scene.v().setSootClassPath(sootClassPath);
//		Options.v().set_soot_classpath(appiumPath+":"+sootClassPath);
		Options.v().set_keep_line_number(true);
		Options.v().set_allow_phantom_refs(true);
		sootClass = Scene.v().loadClassAndSupport(className);
		Scene.v().loadNecessaryClasses();
		sootClass.setApplicationClass();
	}
	
//	$r11 can contrain $r1...
	public static String getKeyInStmt(Map<String, String> guiMap, String stmt){
		for(String key: guiMap.keySet()){
			if(stmt.endsWith(key)){
				return key;
			}
		}
		return null;
	}
	
	public static String getStrInBrackets(String str){
		Matcher m = Pattern.compile("\\(([^)]+)\\)").matcher(str);
	     while(m.find()) {
	       return m.group(1);    
	     }
	     return null;
	}
	
	public static String getStrInQuotes(String str){
		Matcher m = Pattern.compile("\"([^\"]*)\"").matcher(str);
	     while(m.find()) {
	       return m.group(1);    
	     }
	     return null;
	}
}
