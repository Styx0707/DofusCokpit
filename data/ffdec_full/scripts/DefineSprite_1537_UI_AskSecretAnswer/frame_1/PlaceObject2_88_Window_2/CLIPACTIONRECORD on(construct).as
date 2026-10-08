on(construct){
   while(true)
   {
      if(!ord("\x0b"))
      {
         if(!ord("\x0b"))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
      {
         break;
      }
      set("\x16\x18\x14",true);
      contentPath = "UI_AskSecretAnswerContent";
      enabled = true;
      set("\x18\f\t",false);
      §§push("styleName");
      §§push("LightBrownWindow");
      if(!ord("\x06"))
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         §§goto(addr16275);
      }
      break;
   }
   set(§§pop(),§§pop());
   title = "";
   addr16275:
}
