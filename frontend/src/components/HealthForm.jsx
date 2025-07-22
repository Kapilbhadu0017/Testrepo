import { useState, forwardRef, useImperativeHandle } from "react";

const symptomOptions = [
 "Coughing", "Sneezing", "Wheezing", "Shortness of breath", "Headache",
 "Fatigue", "Eye irritation", "Sore throat", "Runny nose", "Chest tightness",
 "Dizziness", "Fever", "Allergies", "Itchy skin", "Nasal congestion", "Breathing difficulty",
 "Dry throat", "Skin rashes", "Irritability", "Loss of smell", "Tight chest",
 "Nausea", "Burning eyes", "Sinus pressure", "Rapid heartbeat"
];

const addictionOptions = [
 "Smoking", "Alcohol", "Caffeine", "Sugar", "Social Media", "Gaming", "Gambling", "None"
];

const HealthForm = forwardRef(({ aqiValue = 0, onGetAIAdvice, loading = false, theme = 'light' }, ref) => {
 const [selected, setSelected] = useState([]);
 const [notes, setNotes] = useState("");
 const [age, setAge] = useState("");
 const [conditions, setConditions] = useState([]);
 const [addictions, setAddictions] = useState([]);

 const toggleSymptom = (symptom) => {
   setSelected((prev) =>
     prev.includes(symptom)
       ? prev.filter((s) => s !== symptom)
       : [...prev, symptom]
   );
 };

 const toggleAddiction = (addiction) => {
   setAddictions((prev) => {
     if (addiction === "None") {
       return prev.includes("None") ? [] : ["None"];
     } else {
       const newAddictions = prev.includes("None") 
         ? prev.filter(a => a !== "None")
         : prev;
       
       return newAddictions.includes(addiction)
         ? newAddictions.filter(a => a !== addiction)
         : [...newAddictions, addiction];
     }
   });
 };

 // Expose form data to parent component
 useImperativeHandle(ref, () => ({
   getFormData: () => ({
     selected,
     notes,
     age,
     conditions,
     addictions
   })
 }));

 const isDark = theme === 'dark';

 return (
   <section
     id="health-form"
     className={`p-6 max-w-4xl mx-auto mt-8 rounded-lg transition-all duration-300 ${
       isDark 
         ? 'bg-gradient-to-r from-blue-900/30 to-purple-900/30 backdrop-blur-md' 
         : 'bg-white/80 border-2 border-green-200/50 shadow-xl backdrop-blur-lg'
     }`}
     aria-labelledby="health-form-title"
   >
     <header className="mb-8 text-center">
       <h2 id="health-form-title" className={`text-3xl font-bold mb-2 bg-clip-text text-transparent ${
         isDark
           ? 'bg-gradient-to-r from-purple-400 to-pink-400'
           : 'bg-gradient-to-r from-green-600 to-teal-500'
       }`}>
         Health Assessment
       </h2>
       <p className={`${isDark ? 'text-gray-300' : 'text-gray-800'}`}>
         Tell us how you're feeling to get personalized AI health advice
       </p>
     </header>

     <form
       className="space-y-8"
       role="form"
       aria-label="Health assessment form"
     >
       <div className="space-y-4">
         <h3 className={`text-xl font-semibold ${isDark ? 'text-green-300' : 'text-green-800'}`}>
           Select your symptoms <span className={`text-sm font-normal ${isDark ? 'text-green-400' : 'text-green-600'}`}>(select all that apply)</span>
         </h3>
         <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
           {symptomOptions.map((symptom) => {
             const isSelected = selected.includes(symptom);
             return (
               <label 
                 key={symptom} 
                 className={`
                   flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 cursor-pointer group
                   ${isDark 
                     ? 'bg-gray-800/50 border-gray-600/30 hover:border-purple-500/50' 
                     : 'bg-white border-gray-300 hover:border-green-400 shadow-sm'
                   }
                   ${isSelected && (isDark ? 'border-purple-500 bg-purple-900/20' : 'border-green-500 bg-green-50')}
                 `}
               >
                 <input
                   type="checkbox"
                   checked={isSelected}
                   onChange={() => toggleSymptom(symptom)}
                   aria-label={`Select ${symptom} symptom`}
                   className="checkbox-futuristic"
                 />
                 <span className={`
                   text-sm transition-colors
                   ${isDark 
                     ? 'text-gray-300 group-hover:text-purple-300' 
                     : 'text-gray-700 group-hover:text-green-600'
                   }
                   ${isSelected && (isDark ? 'text-purple-200' : 'text-green-800 font-semibold')}
                 `}>{symptom}</span>
               </label>
             );
           })}
         </div>
         {selected.length > 0 && (
           <p className={`text-sm mt-2 font-semibold ${isDark ? 'text-purple-300' : 'text-green-800'}`}>
             Selected: {selected.length} symptom{selected.length !== 1 ? 's' : ''}
           </p>
         )}
       </div>

       <div className="space-y-4">
         <h3 className={`text-xl font-semibold ${isDark ? 'text-green-300' : 'text-green-800'}`}>
           Pre-existing Conditions <span className={`text-sm font-normal ${isDark ? 'text-green-400' : 'text-green-600'}`}>(select all that apply)</span>
         </h3>
         <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
           {["Asthma", "Heart Disease", "Diabetes", "Hypertension", "None"].map((cond) => {
             const isSelected = conditions.includes(cond);
             return (
               <label 
                 key={cond} 
                 className={`
                   flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 cursor-pointer group
                   ${isDark 
                     ? 'bg-gray-800/50 border-gray-600/30 hover:border-purple-500/50' 
                     : 'bg-white border-gray-300 hover:border-green-400 shadow-sm'
                   }
                   ${isSelected && (isDark ? 'border-purple-500 bg-purple-900/20' : 'border-green-500 bg-green-50')}
                 `}
               >
                 <input
                   type="checkbox"
                   value={cond}
                   checked={isSelected}
                   onChange={(e) => {
                     const checked = e.target.checked;

                     if (cond === "None") {
                       setConditions(checked ? ["None"] : []);
                     } else {
                       const newConditions = checked
                         ? [...conditions.filter((c) => c !== "None"), cond]
                         : conditions.filter((c) => c !== cond);

                       setConditions(newConditions);
                     }
                   }}
                   aria-label={`Select ${cond} condition`}
                   className="checkbox-futuristic"
                 />
                 <span className={`
                   text-sm transition-colors
                   ${isDark 
                     ? 'text-gray-300 group-hover:text-purple-300' 
                     : 'text-gray-700 group-hover:text-green-600'
                   }
                   ${isSelected && (isDark ? 'text-purple-200' : 'text-green-800 font-semibold')}
                 `}>{cond}</span>
               </label>
             );
           })}
         </div>
         {conditions.length > 0 && (
           <p className={`text-sm mt-2 font-semibold ${isDark ? 'text-purple-300' : 'text-green-800'}`}>
             Selected: {conditions.join(', ')}
           </p>
         )}
       </div>

       <div className="space-y-2">
         <h3 className={`text-xl font-semibold ${isDark ? 'text-green-300' : 'text-green-800'}`}>
           Your Age <span className={`text-sm font-normal ${isDark ? 'text-green-400' : 'text-green-600'}`}>(optional)</span>
         </h3>
         <input
           id="age-input"
           type="number"
           value={age}
           onChange={(e) => setAge(e.target.value)}
           onWheel={(e) => e.target.blur()}
           onKeyDown={(e) => {
             if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
               e.preventDefault();
             }
           }}
           className={`w-full p-4 rounded-lg text-lg transition-all duration-300 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none ${
             isDark 
               ? 'input-futuristic' 
               : 'border border-gray-300 bg-white text-gray-900 focus:border-purple-400 focus:ring-2 focus:ring-purple-200'
           }`}
           placeholder="Enter your age"
           min="0"
           max="150"
           aria-describedby="age-help"
         />
         <div id="age-help" className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
           Your age helps us provide more personalized health recommendations
         </div>
       </div>

       <div className="space-y-4">
         <h3 className={`text-xl font-semibold ${isDark ? 'text-green-300' : 'text-green-800'}`}>
           Addictions <span className={`text-sm font-normal ${isDark ? 'text-green-400' : 'text-green-600'}`}>(select all that apply)</span>
         </h3>
         <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
           {addictionOptions.map((addiction) => {
             const isSelected = addictions.includes(addiction);
             return (
               <label 
                 key={addiction} 
                 className={`
                   flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 cursor-pointer group
                   ${isDark 
                     ? 'bg-gray-800/50 border-gray-600/30 hover:border-purple-500/50' 
                     : 'bg-white border-gray-300 hover:border-green-400 shadow-sm'
                   }
                   ${isSelected && (isDark ? 'border-purple-500 bg-purple-900/20' : 'border-green-500 bg-green-50')}
                 `}
               >
                 <input
                   type="checkbox"
                   checked={isSelected}
                   onChange={() => toggleAddiction(addiction)}
                   aria-label={`Select ${addiction} addiction`}
                   className="checkbox-futuristic"
                 />
                 <span className={`
                   text-sm transition-colors
                   ${isDark 
                     ? 'text-gray-300 group-hover:text-purple-300' 
                     : 'text-gray-700 group-hover:text-green-600'
                   }
                   ${isSelected && (isDark ? 'text-purple-200' : 'text-green-800 font-semibold')}
                 `}>{addiction}</span>
               </label>
             );
           })}
         </div>
         {addictions.length > 0 && (
           <p className={`text-sm mt-2 font-semibold ${isDark ? 'text-purple-300' : 'text-green-800'}`}>
             Selected: {addictions.join(', ')}
           </p>
         )}
         <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
           💡 Vayu AI will analyze how these addictions may interact with your symptoms and air quality
         </div>
       </div>

       <div className="space-y-2">
         <h3 className={`text-xl font-semibold ${isDark ? 'text-green-300' : 'text-green-800'}`}>
           Additional Notes <span className={`text-sm font-normal ${isDark ? 'text-green-400' : 'text-green-600'}`}>(optional)</span>
         </h3>
         <textarea
           id="notes-input"
           className={`w-full p-4 rounded-lg resize-none transition-all duration-300 ${
             isDark 
               ? 'input-futuristic' 
               : 'border border-gray-300 bg-white text-gray-900 focus:border-purple-400 focus:ring-2 focus:ring-purple-200'
           }`}
           placeholder="Any other health concerns, medications, or symptoms you'd like to mention..."
           value={notes}
           onChange={(e) => setNotes(e.target.value)}
           rows="4"
           aria-describedby="notes-help"
         />
         <div id="notes-help" className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
           Provide any additional context that might help with your health assessment
         </div>
       </div>

       <div className="pt-4 text-center">
         <button
           type="button"
           onClick={onGetAIAdvice}
           disabled={loading}
           className={`px-8 py-4 rounded-lg shadow-2xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 mx-auto ${
             isDark 
               ? 'bg-gradient-to-r from-purple-600 to-pink-600 neon-glow-pink text-white' 
               : 'bg-gradient-to-r from-green-500 to-teal-500 shadow-lg text-white'
           }`}
           aria-label="Get AI health advice"
         >
           {loading ? (
             <>
               <div className="spinner-futuristic w-5 h-5" aria-hidden="true"></div>
               <span className="text-white font-semibold">Getting Advice...</span>
             </>
           ) : (
             <>
               <span className="text-white text-xl font-bold">AI</span>
               <span className="text-white font-semibold">Get Health Advice</span>
             </>
           )}
         </button>
         <p className={`text-sm mt-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
           💡 Get personalized AI health advice based on your symptoms and current air quality
         </p>
       </div>
     </form>
   </section>
 );
});

export default HealthForm;